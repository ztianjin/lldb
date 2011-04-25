//===-- UnwindAssembly-x86.h -------------------------------------*- C++ -*-===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#ifndef liblldb_UnwindAssembly_x86_h_
#define liblldb_UnwindAssembly_x86_h_

#include "lldb/lldb-private.h"
#include "lldb/Target/UnwindAssembly.h"
#include "lldb/Target/Thread.h"

namespace lldb_private {
    
class UnwindAssembly_x86 : public lldb_private::UnwindAssembly
{
public:

    ~UnwindAssembly_x86 () { }

    virtual bool
    GetNonCallSiteUnwindPlanFromAssembly (AddressRange& func, lldb_private::Thread& thread, UnwindPlan& unwind_plan);

    virtual bool
    GetFastUnwindPlan (AddressRange& func, lldb_private::Thread& thread, UnwindPlan &unwind_plan);

    // thread may be NULL in which case we only use the Target (e.g. if this is called pre-process-launch).
    virtual bool
    FirstNonPrologueInsn (AddressRange& func, lldb_private::Target& target, lldb_private::Thread* thread, Address& first_non_prologue_insn);

    static lldb_private::UnwindAssembly *
    CreateInstance (const lldb_private::ArchSpec &arch);


    //------------------------------------------------------------------
    // PluginInterface protocol
    //------------------------------------------------------------------
    static void
    Initialize();

    static void
    Terminate();

    static const char *
    GetPluginNameStatic();

    static const char *
    GetPluginDescriptionStatic();

    virtual const char *
    GetPluginName();
    
    virtual const char *
    GetShortPluginName();
    
    virtual uint32_t
    GetPluginVersion();
    
private:
    UnwindAssembly_x86(int cpu) : 
          lldb_private::UnwindAssembly(), m_cpu(cpu) { } // Call CreateInstance instead.

    int m_cpu;
};


} // namespace lldb_private

#endif // liblldb_UnwindAssembly_x86_h_