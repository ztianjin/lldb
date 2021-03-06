import lldb
import lldb.formatters.Logger

# libcxx STL formatters for LLDB
# These formatters are based upon the implementation of libc++ that
# ships with current releases of OS X - They will not work for other implementations
# of the standard C++ library - and they are bound to use the libc++-specific namespace

# this could probably be made more efficient but since it only reads a handful of bytes at a time
# we probably don't need to worry too much about this for the time being
def make_string(F,L):
	strval = ''
	G = F.GetData().uint8
	for X in range(L):
		V = G[X]
		if V == 0:
			break
		strval = strval + chr(V % 256)
	return '"' + strval + '"'

# if we ever care about big-endian, these two functions might need to change
def is_short_string(value):
	return True if (value & 1) == 0 else False
def extract_short_size(value):
	return ((value >> 1) % 256)

# some of the members of libc++ std::string are anonymous or have internal names that convey
# no external significance - we access them by index since this saves a name lookup that would add
# no information for readers of the code, but when possible try to use meaningful variable names
def stdstring_SummaryProvider(valobj,dict):
	logger = lldb.formatters.Logger.Logger()
	r = valobj.GetChildAtIndex(0)
	B = r.GetChildAtIndex(0)
	first = B.GetChildAtIndex(0)
	D = first.GetChildAtIndex(0)
	l = D.GetChildAtIndex(0)
	s = D.GetChildAtIndex(1)
	D20 = s.GetChildAtIndex(0)
	size_mode = D20.GetChildAtIndex(0).GetValueAsUnsigned(0)
	if is_short_string(size_mode):
		size = extract_short_size(size_mode)
		return make_string(s.GetChildAtIndex(1),size)
	else:
		data_ptr = l.GetChildAtIndex(2)
		size_vo = l.GetChildAtIndex(1)
		size = size_vo.GetValueAsUnsigned(0)+1 # the NULL terminator must be accounted for
		if size <= 1: # should never be the case
			return '""'
		data = data_ptr.GetPointeeData(0,size)
		error = lldb.SBError()
		strval = data.GetString(error,0)
		if error.Fail():
			return '<error:' + error.GetCString() + '>'
		else:
			return '"' + strval + '"'

class stdvector_SynthProvider:

	def __init__(self, valobj, dict):
		logger = lldb.formatters.Logger.Logger()
		self.valobj = valobj;

	def num_children(self):
		logger = lldb.formatters.Logger.Logger()
		try:
			start_val = self.start.GetValueAsUnsigned(0)
			finish_val = self.finish.GetValueAsUnsigned(0)
			# Before a vector has been constructed, it will contain bad values
			# so we really need to be careful about the length we return since
			# unitialized data can cause us to return a huge number. We need
			# to also check for any of the start, finish or end of storage values
			# being zero (NULL). If any are, then this vector has not been 
			# initialized yet and we should return zero

			# Make sure nothing is NULL
			if start_val == 0 or finish_val == 0:
				return 0
			# Make sure start is less than finish
			if start_val >= finish_val:
				return 0

			num_children = (finish_val-start_val)
			if (num_children % self.data_size) != 0:
				return 0
			else:
				num_children = num_children/self.data_size
			return num_children
		except:
			return 0;

	def get_child_index(self,name):
		logger = lldb.formatters.Logger.Logger()
		try:
			return int(name.lstrip('[').rstrip(']'))
		except:
			return -1

	def get_child_at_index(self,index):
		logger = lldb.formatters.Logger.Logger()
		logger >> "Retrieving child " + str(index)
		if index < 0:
			return None;
		if index >= self.num_children():
			return None;
		try:
			offset = index * self.data_size
			return self.start.CreateChildAtOffset('['+str(index)+']',offset,self.data_type)
		except:
			return None

	def update(self):
		logger = lldb.formatters.Logger.Logger()
		try:
			self.start = self.valobj.GetChildMemberWithName('__begin_')
			self.finish = self.valobj.GetChildMemberWithName('__end_')
			# the purpose of this field is unclear, but it is the only field whose type is clearly T* for a vector<T>
			# if this ends up not being correct, we can use the APIs to get at template arguments
			data_type_finder = self.valobj.GetChildMemberWithName('__end_cap_').GetChildMemberWithName('__first_')
			self.data_type = data_type_finder.GetType().GetPointeeType()
			self.data_size = self.data_type.GetByteSize()
		except:
			pass

# Just an example: the actual summary is produced by a summary string: size=${svar%#}
def stdvector_SummaryProvider(valobj,dict):
	prov = stdvector_SynthProvider(valobj,None)
	return 'size=' + str(prov.num_children())

class stdlist_entry:

	def __init__(self,entry):
		logger = lldb.formatters.Logger.Logger()
		self.entry = entry

	def _next_impl(self):
		logger = lldb.formatters.Logger.Logger()
		return stdlist_entry(self.entry.GetChildMemberWithName('__next_'))

	def _prev_impl(self):
		logger = lldb.formatters.Logger.Logger()
		return stdlist_entry(self.entry.GetChildMemberWithName('__prev_'))

	def _value_impl(self):
		logger = lldb.formatters.Logger.Logger()
		return self.entry.GetValueAsUnsigned(0)

	def _isnull_impl(self):
		logger = lldb.formatters.Logger.Logger()
		return self._value_impl() == 0

	def _sbvalue_impl(self):
		logger = lldb.formatters.Logger.Logger()
		return self.entry

	next = property(_next_impl,None)
	value = property(_value_impl,None)
	is_null = property(_isnull_impl,None)
	sbvalue = property(_sbvalue_impl,None)

class stdlist_iterator:

	def increment_node(self,node):
		logger = lldb.formatters.Logger.Logger()
		if node.is_null:
			return None
		return node.next

	def __init__(self,node):
		logger = lldb.formatters.Logger.Logger()
		self.node = stdlist_entry(node) # we convert the SBValue to an internal node object on entry

	def value(self):
		logger = lldb.formatters.Logger.Logger()
		return self.node.sbvalue # and return the SBValue back on exit

	def next(self):
		logger = lldb.formatters.Logger.Logger()
		node = self.increment_node(self.node)
		if node != None and node.sbvalue.IsValid() and not(node.is_null):
			self.node = node
			return self.value()
		else:
			return None

	def advance(self,N):
		logger = lldb.formatters.Logger.Logger()
		if N < 0:
			return None
		if N == 0:
			return self.value()
		if N == 1:
			return self.next()
		while N > 0:
			self.next()
			N = N - 1
		return self.value()


class stdlist_SynthProvider:
	def __init__(self, valobj, dict):
		logger = lldb.formatters.Logger.Logger()
		self.valobj = valobj

	def next_node(self,node):
		logger = lldb.formatters.Logger.Logger()
		return node.GetChildMemberWithName('__next_')

	def value(self,node):
		logger = lldb.formatters.Logger.Logger()
		return node.GetValueAsUnsigned()

	# Floyd's cyle-finding algorithm
	# try to detect if this list has a loop
	def has_loop(self):
		global _list_uses_loop_detector
		logger = lldb.formatters.Logger.Logger()
		if _list_uses_loop_detector == False:
			logger >> "Asked not to use loop detection"
			return False
		slow = stdlist_entry(self.head)
		fast1 = stdlist_entry(self.head)
		fast2 = stdlist_entry(self.head)
		while slow.next.value != self.node_address:
			slow_value = slow.value
			fast1 = fast2.next
			fast2 = fast1.next
			if fast1.value == slow_value or fast2.value == slow_value:
				return True
			slow = slow.next
		return False

	def num_children(self):
		global _list_capping_size
		logger = lldb.formatters.Logger.Logger()
		if self.count == None:
			self.count = self.num_children_impl()
			if self.count > _list_capping_size:
				self.count = _list_capping_size
		return self.count

	def num_children_impl(self):
		global _list_capping_size
		logger = lldb.formatters.Logger.Logger()
		try:
			next_val = self.head.GetValueAsUnsigned(0)
			prev_val = self.tail.GetValueAsUnsigned(0)
			# After a std::list has been initialized, both next and prev will be non-NULL
			if next_val == 0 or prev_val == 0:
				return 0
			if next_val == self.node_address:
				return 0
			if next_val == prev_val:
				return 1
			if self.has_loop():
				return 0
			size = 2
			current = stdlist_entry(self.head)
			while current.next.value != self.node_address:
				size = size + 1
				current = current.next
				if size > _list_capping_size:
					return _list_capping_size
			return (size - 1)
		except:
			return 0;

	def get_child_index(self,name):
		logger = lldb.formatters.Logger.Logger()
		try:
			return int(name.lstrip('[').rstrip(']'))
		except:
			return -1

	def get_child_at_index(self,index):
		logger = lldb.formatters.Logger.Logger()
		logger >> "Fetching child " + str(index)
		if index < 0:
			return None;
		if index >= self.num_children():
			return None;
		try:
			current = stdlist_iterator(self.head)
			current = current.advance(index)
			# we do not return __value_ because then all our children would be named __value_
			# we need to make a copy of __value__ with the right name - unfortunate
			obj = current.GetChildMemberWithName('__value_')
			obj_data = obj.GetData()
			return self.valobj.CreateValueFromData('[' + str(index) + ']',obj_data,self.data_type)
		except:
			return None

	def extract_type(self):
		logger = lldb.formatters.Logger.Logger()
		list_type = self.valobj.GetType().GetUnqualifiedType()
		if list_type.IsReferenceType():
			list_type = list_type.GetDereferencedType()
		if list_type.GetNumberOfTemplateArguments() > 0:
			data_type = list_type.GetTemplateArgumentType(0)
		else:
			data_type = None
		return data_type

	def update(self):
		logger = lldb.formatters.Logger.Logger()
		self.count = None
		try:
			impl = self.valobj.GetChildMemberWithName('__end_')
			self.node_address = self.valobj.AddressOf().GetValueAsUnsigned(0)
			self.head = impl.GetChildMemberWithName('__next_')
			self.tail = impl.GetChildMemberWithName('__prev_')
			self.data_type = self.extract_type()
			self.data_size = self.data_type.GetByteSize()
		except:
			pass

# Just an example: the actual summary is produced by a summary string: size=${svar%#}
def stdlist_SummaryProvider(valobj,dict):
	prov = stdlist_SynthProvider(valobj,None)
	return 'size=' + str(prov.num_children())

# a tree node - this class makes the syntax in the actual iterator nicer to read and maintain
class stdmap_iterator_node:
	def _left_impl(self):
		logger = lldb.formatters.Logger.Logger()
		return stdmap_iterator_node(self.node.GetChildMemberWithName("__left_"))

	def _right_impl(self):
		logger = lldb.formatters.Logger.Logger()
		return stdmap_iterator_node(self.node.GetChildMemberWithName("__right_"))

	def _parent_impl(self):
		logger = lldb.formatters.Logger.Logger()
		return stdmap_iterator_node(self.node.GetChildMemberWithName("__parent_"))

	def _value_impl(self):
		logger = lldb.formatters.Logger.Logger()
		return self.node.GetValueAsUnsigned(0)

	def _sbvalue_impl(self):
		logger = lldb.formatters.Logger.Logger()
		return self.node

	def _null_impl(self):
		logger = lldb.formatters.Logger.Logger()
		return self.value == 0

	def __init__(self,node):
		logger = lldb.formatters.Logger.Logger()
		self.node = node

	left = property(_left_impl,None)
	right = property(_right_impl,None)
	parent = property(_parent_impl,None)
	value = property(_value_impl,None)
	is_null = property(_null_impl,None)
	sbvalue = property(_sbvalue_impl,None)

# a Python implementation of the tree iterator used by libc++
class stdmap_iterator:

	def tree_min(self,x):
		logger = lldb.formatters.Logger.Logger()
		steps = 0
		if x.is_null:
			return None
		while (not x.left.is_null):
			x = x.left
			steps += 1
			if steps > self.max_count:
				logger >> "Returning None - we overflowed"
				return None
		return x

	def tree_max(self,x):
		logger = lldb.formatters.Logger.Logger()
		if x.is_null:
			return None
		while (not x.right.is_null):
			x =  x.right
		return x

	def tree_is_left_child(self,x):
		logger = lldb.formatters.Logger.Logger()
		if x.is_null:
			return None
		return True if x.value == x.parent.left.value else False

	def increment_node(self,node):
		logger = lldb.formatters.Logger.Logger()
		if node.is_null:
			return None
		if not node.right.is_null:
			return self.tree_min(node.right)
		steps = 0
		while (not self.tree_is_left_child(node)):
			steps += 1
			if steps > self.max_count:
				logger >> "Returning None - we overflowed"
				return None
			node = node.parent
		return node.parent

	def __init__(self,node,max_count=0):
		logger = lldb.formatters.Logger.Logger()
		self.node = stdmap_iterator_node(node) # we convert the SBValue to an internal node object on entry
		self.max_count = max_count

	def value(self):
		logger = lldb.formatters.Logger.Logger()
		return self.node.sbvalue # and return the SBValue back on exit

	def next(self):
		logger = lldb.formatters.Logger.Logger()
		node = self.increment_node(self.node)
		if node != None and node.sbvalue.IsValid() and not(node.is_null):
			self.node = node
			return self.value()
		else:
			return None

	def advance(self,N):
		logger = lldb.formatters.Logger.Logger()
		if N < 0:
			return None
		if N == 0:
			return self.value()
		if N == 1:
			return self.next()
		while N > 0:
			if self.next() == None:
				return None
			N = N - 1
		return self.value()

class stdmap_SynthProvider:

	def __init__(self, valobj, dict):
		logger = lldb.formatters.Logger.Logger()
		self.valobj = valobj;
		self.pointer_size = self.valobj.GetProcess().GetAddressByteSize()

	def update(self):
		logger = lldb.formatters.Logger.Logger()
		self.count = None
		try:
			# we will set this to True if we find out that discovering a node in the map takes more steps than the overall size of the RB tree
			# if this gets set to True, then we will merrily return None for any child from that moment on
			self.garbage = False
			self.tree = self.valobj.GetChildMemberWithName('__tree_')
			self.root_node = self.tree.GetChildMemberWithName('__begin_node_')
			# this data is either lazily-calculated, or cannot be inferred at this moment
			# we still need to mark it as None, meaning "please set me ASAP"
			self.data_type = None
			self.data_size = None
			self.skip_size = None
		except:
			pass

	def num_children(self):
		global _map_capping_size
		logger = lldb.formatters.Logger.Logger()
		if self.count == None:
			self.count = self.num_children_impl()
			if self.count > _map_capping_size:
				self.count = _map_capping_size
		return self.count

	def num_children_impl(self):
		logger = lldb.formatters.Logger.Logger()
		try:
			return self.valobj.GetChildMemberWithName('__tree_').GetChildMemberWithName('__pair3_').GetChildMemberWithName('__first_').GetValueAsUnsigned()
		except:
			return 0;

	def get_data_type(self):
		logger = lldb.formatters.Logger.Logger()
		if self.data_type == None or self.data_size == None:
			if self.num_children() == 0:
				return False
			deref = self.root_node.Dereference()
			if not(deref.IsValid()):
				return False
			value = deref.GetChildMemberWithName('__value_')
			if not(value.IsValid()):
				return False
			self.data_type = value.GetType()
			self.data_size = self.data_type.GetByteSize()
			self.skip_size = None
			return True
		else:
			return True

	def get_value_offset(self,node):
		logger = lldb.formatters.Logger.Logger()
		if self.skip_size == None:
			node_type = node.GetType()
			fields_count = node_type.GetNumberOfFields()
			for i in range(fields_count):
				field = node_type.GetFieldAtIndex(i)
				if field.GetName() == '__value_':
					self.skip_size = field.GetOffsetInBytes()
					break
		return (self.skip_size != None)

	def get_child_index(self,name):
		logger = lldb.formatters.Logger.Logger()
		try:
			return int(name.lstrip('[').rstrip(']'))
		except:
			return -1

	def get_child_at_index(self,index):
		logger = lldb.formatters.Logger.Logger()
		logger >> "Retrieving child " + str(index)
		if index < 0:
			return None
		if index >= self.num_children():
			return None;
		if self.garbage:
			logger >> "Returning None since this tree is garbage"
			return None
		try:
			iterator = stdmap_iterator(self.root_node,max_count=self.num_children())
			# the debug info for libc++ std::map is such that __begin_node_ has a very nice and useful type
			# out of which we can grab the information we need - every other node has a less informative
			# type which omits all value information and only contains housekeeping information for the RB tree
			# hence, we need to know if we are at a node != 0, so that we can still get at the data
			need_to_skip = (index > 0)
			current = iterator.advance(index)
			if current == None:
				logger >> "Tree is garbage - returning None"
				self.garbage = True
				return None
			if self.get_data_type():
				if not(need_to_skip):
					current = current.Dereference()
					obj = current.GetChildMemberWithName('__value_')
					obj_data = obj.GetData()
					self.get_value_offset(current) # make sure we have a valid offset for the next items
					# we do not return __value_ because then we would end up with a child named
					# __value_ instead of [0]
					return self.valobj.CreateValueFromData('[' + str(index) + ']',obj_data,self.data_type)
				else:
					# FIXME we need to have accessed item 0 before accessing any other item!
					if self.skip_size == None:
						logger >> "You asked for item > 0 before asking for item == 0, too bad - I have no clue"
						return None
					return current.CreateChildAtOffset('[' + str(index) + ']',self.skip_size,self.data_type)
			else:
				logger >> "Unable to infer data-type - returning None (should mark tree as garbage here?)"
				return None
		except Exception as err:
			logger >> "Hit an exception: " + str(err)
			return None

# Just an example: the actual summary is produced by a summary string: size=${svar%#}
def stdmap_SummaryProvider(valobj,dict):
	prov = stdmap_SynthProvider(valobj,None)
	return 'size=' + str(prov.num_children())


# we can use two different categories for old and new formatters - type names are different enough that we should make no confusion
# talking with libc++ developer: "std::__1::class_name is set in stone until we decide to change the ABI. That shouldn't happen within a 5 year time frame"
def __lldb_init_module(debugger,dict):
	debugger.HandleCommand('type summary add -F libcxx.stdstring_SummaryProvider "std::__1::string" -w libcxx')
	debugger.HandleCommand('type summary add -F libcxx.stdstring_SummaryProvider "std::__1::basic_string<char, class std::__1::char_traits<char>, class std::__1::allocator<char> >" -w libcxx')
	debugger.HandleCommand('type synthetic add -l libcxx.stdvector_SynthProvider -x "^(std::__1::)vector<.+>$" -w libcxx')
	debugger.HandleCommand('type summary add -F libcxx.stdvector_SummaryProvider -e -x "^(std::__1::)vector<.+>$" -w libcxx')
	debugger.HandleCommand('type synthetic add -l libcxx.stdlist_SynthProvider -x "^(std::__1::)list<.+>$" -w libcxx')
	debugger.HandleCommand('type summary add -F libcxx.stdlist_SummaryProvider -e -x "^(std::__1::)list<.+>$" -w libcxx')
	debugger.HandleCommand('type synthetic add -l libcxx.stdmap_SynthProvider -x "^(std::__1::)map<.+> >$" -w libcxx')
	debugger.HandleCommand('type summary add -F libcxx.stdmap_SummaryProvider -e -x "^(std::__1::)map<.+> >$" -w libcxx')
	debugger.HandleCommand("type category enable libcxx")

_map_capping_size = 255
_list_capping_size = 255
_list_uses_loop_detector = True
