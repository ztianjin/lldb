//===-- SWIG Interface for SBValue ------------------------------*- C++ -*-===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

namespace lldb {

%feature("docstring",
"Represents the value of a variable, a register, or an expression.

SBValue supports iteration through its child, which in turn is represented
as an SBValue.  For example, we can get the general purpose registers of a
frame as an SBValue, and iterate through all the registers,

    registerSet = frame.GetRegisters() # Returns an SBValueList.
    for regs in registerSet:
        if 'general purpose registers' in regs.getName().lower():
            GPRs = regs
            break

    print '%s (number of children = %d):' % (GPRs.GetName(), GPRs.GetNumChildren())
    for reg in GPRs:
        print 'Name: ', reg.GetName(), ' Value: ', reg.GetValue()

produces the output:

General Purpose Registers (number of children = 21):
Name:  rax  Value:  0x0000000100000c5c
Name:  rbx  Value:  0x0000000000000000
Name:  rcx  Value:  0x00007fff5fbffec0
Name:  rdx  Value:  0x00007fff5fbffeb8
Name:  rdi  Value:  0x0000000000000001
Name:  rsi  Value:  0x00007fff5fbffea8
Name:  rbp  Value:  0x00007fff5fbffe80
Name:  rsp  Value:  0x00007fff5fbffe60
Name:  r8  Value:  0x0000000008668682
Name:  r9  Value:  0x0000000000000000
Name:  r10  Value:  0x0000000000001200
Name:  r11  Value:  0x0000000000000206
Name:  r12  Value:  0x0000000000000000
Name:  r13  Value:  0x0000000000000000
Name:  r14  Value:  0x0000000000000000
Name:  r15  Value:  0x0000000000000000
Name:  rip  Value:  0x0000000100000dae
Name:  rflags  Value:  0x0000000000000206
Name:  cs  Value:  0x0000000000000027
Name:  fs  Value:  0x0000000000000010
Name:  gs  Value:  0x0000000000000048"
) SBValue;
class SBValue
{
public:
    SBValue ();

    SBValue (const SBValue &rhs);

    ~SBValue ();

    bool
    IsValid() const;
    
    SBError
    GetError();

    lldb::user_id_t
    GetID ();
    
    const char *
    GetName();

    const char *
    GetTypeName ();

    size_t
    GetByteSize ();

    bool
    IsInScope (const lldb::SBFrame &frame);  // DEPRECATED - SBValues know their own frames.

    bool
    IsInScope ();

    lldb::Format
    GetFormat () const;
    
    void
    SetFormat (lldb::Format format);

    const char *
    GetValue (const lldb::SBFrame &frame);   // DEPRECATED - SBValues know their own frames.

    const char *
    GetValue ();

    ValueType
    GetValueType ();

    bool
    GetValueDidChange (const lldb::SBFrame &frame);  // DEPRECATED - SBValues know their own frames.

    bool
    GetValueDidChange ();

    const char *
    GetSummary (const lldb::SBFrame &frame);  // DEPRECATED - SBValues know their own frames.
    
    const char *
    GetSummary ();
    
    const char *
    GetObjectDescription (const lldb::SBFrame &frame);  // DEPRECATED - SBValues know their own frames.

    const char *
    GetObjectDescription ();

    const char *
    GetLocation (const lldb::SBFrame &frame);  // DEPRECATED - SBValues know their own frames.

    const char *
    GetLocation ();

    bool
    SetValueFromCString (const lldb::SBFrame &frame, const char *value_str);  // DEPRECATED - SBValues know their own frames.

    bool
    SetValueFromCString (const char *value_str);

    lldb::SBValue
    GetChildAtIndex (uint32_t idx);

    %feature("docstring", "
    //------------------------------------------------------------------
    /// Get a child value by index from a value.
    ///
    /// Structs, unions, classes, arrays and and pointers have child
    /// values that can be access by index. 
    ///
    /// Structs and unions access child members using a zero based index
    /// for each child member. For
    /// 
    /// Classes reserve the first indexes for base classes that have 
    /// members (empty base classes are omitted), and all members of the
    /// current class will then follow the base classes. 
    ///
    /// Pointers differ depending on what they point to. If the pointer
    /// points to a simple type, the child at index zero
    /// is the only child value available, unless \a synthetic_allowed 
    /// is \b true, in which case the pointer will be used as an array
    /// and can create 'synthetic' child values using positive or 
    /// negative indexes. If the pointer points to an aggregate type 
    /// (an array, class, union, struct), then the pointee is 
    /// transparently skipped and any children are going to be the indexes
    /// of the child values within the aggregate type. For example if
    /// we have a 'Point' type and we have a SBValue that contains a
    /// pointer to a 'Point' type, then the child at index zero will be
    /// the 'x' member, and the child at index 1 will be the 'y' member
    /// (the child at index zero won't be a 'Point' instance).
    /// 
    /// Arrays have a preset number of children that can be accessed by
    /// index and will returns invalid child values for indexes that are
    /// out of bounds unless the \a synthetic_allowed is \b true. In this
    /// case the array can create 'synthetic' child values for indexes 
    /// that aren't in the array bounds using positive or negative 
    /// indexes.
    ///
    /// @param[in] idx
    ///     The index of the child value to get
    ///
    /// @param[in] use_dynamic
    ///     An enumeration that specifies wether to get dynamic values,
    ///     and also if the target can be run to figure out the dynamic
    ///     type of the child value.
    ///
    /// @param[in] synthetic_allowed
    ///     If \b true, then allow child values to be created by index
    ///     for pointers and arrays for indexes that normally wouldn't
    ///     be allowed.
    ///
    /// @return
    ///     A new SBValue object that represents the child member value.
    //------------------------------------------------------------------
    ") GetChildAtIndex;
    lldb::SBValue
    GetChildAtIndex (uint32_t idx, 
                     lldb::DynamicValueType use_dynamic,
                     bool can_create_synthetic);

    %feature("docstring", "
    //------------------------------------------------------------------
    /// Returns the child member index.
    ///
    /// Matches children of this object only and will match base classes and
    /// member names if this is a clang typed object.
    ///
    /// @param[in] name
    ///     The name of the child value to get
    ///
    /// @return
    ///     An index to the child member value.
    //------------------------------------------------------------------
    ") GetIndexOfChildWithName;
    uint32_t
    GetIndexOfChildWithName (const char *name);

    lldb::SBValue
    GetChildMemberWithName (const char *name);

    %feature("docstring", "
    //------------------------------------------------------------------
    /// Returns the child member value.
    ///
    /// Matches child members of this object and child members of any base
    /// classes.
    ///
    /// @param[in] name
    ///     The name of the child value to get
    ///
    /// @param[in] use_dynamic
    ///     An enumeration that specifies wether to get dynamic values,
    ///     and also if the target can be run to figure out the dynamic
    ///     type of the child value.
    ///
    /// @return
    ///     A new SBValue object that represents the child member value.
    //------------------------------------------------------------------
    ") GetChildMemberWithName;
    lldb::SBValue
    GetChildMemberWithName (const char *name, lldb::DynamicValueType use_dynamic);
    
    %feature("docstring", "Expands nested expressions like .a->b[0].c[1]->d."
    ) GetValueForExpressionPath;
    lldb::SBValue
    GetValueForExpressionPath(const char* expr_path);

    uint32_t
    GetNumChildren ();

    void *
    GetOpaqueType();


    lldb::SBValue
    Dereference ();

    bool
    TypeIsPointerType ();

    bool
    GetDescription (lldb::SBStream &description);

    bool
    GetExpressionPath (lldb::SBStream &description);
    
    %feature("docstring", "Returns an expression path for this value."
    ) GetValueForExpressionPath;
    bool
    GetExpressionPath (lldb::SBStream &description, bool qualify_cxx_base_classes);
};

} // namespace lldb