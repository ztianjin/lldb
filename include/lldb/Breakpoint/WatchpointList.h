//===-- WatchpointList.h ----------------------------------------*- C++ -*-===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#ifndef liblldb_WatchpointList_h_
#define liblldb_WatchpointList_h_

// C Includes
// C++ Includes
#include <list>
#include <vector>
// Other libraries and framework includes
// Project includes
#include "lldb/lldb-private.h"
#include "lldb/Core/Address.h"
#include "lldb/Host/Mutex.h"

namespace lldb_private {

//----------------------------------------------------------------------
/// @class WatchpointList WatchpointList.h "lldb/Breakpoint/WatchpointList.h"
/// @brief This class is used by Watchpoint to manage a list of watchpoints,
//  each watchpoint in the list has a unique ID, and is unique by Address as
//  well.
//----------------------------------------------------------------------

class WatchpointList
{
// Only Target can make the watchpoint list, or add elements to it.
// This is not just some random collection of watchpoints.  Rather, the act of
// adding the watchpoint to this list sets its ID.
friend class Watchpoint;
friend class Target;

public:
    //------------------------------------------------------------------
    /// Default constructor makes an empty list.
    //------------------------------------------------------------------
    WatchpointList();

    //------------------------------------------------------------------
    /// Destructor, currently does nothing.
    //------------------------------------------------------------------
    ~WatchpointList();

    //------------------------------------------------------------------
    /// Add a Watchpoint to the list.
    ///
    /// @param[in] wp_sp
    ///    A shared pointer to a watchpoint being added to the list.
    ///
    /// @return
    ///    The ID of the Watchpoint in the list.
    //------------------------------------------------------------------
    lldb::watch_id_t
    Add (const lldb::WatchpointSP& wp_sp);

    //------------------------------------------------------------------
    /// Standard "Dump" method.
    //------------------------------------------------------------------
    void
    Dump (Stream *s) const;

    //------------------------------------------------------------------
    /// Dump with lldb::DescriptionLevel.
    //------------------------------------------------------------------
    void
    DumpWithLevel (Stream *s, lldb::DescriptionLevel description_level) const;

    //------------------------------------------------------------------
    /// Returns a shared pointer to the watchpoint at address
    /// \a addr -
    /// const version.
    ///
    /// @param[in] addr
    ///     The address to look for.
    ///
    /// @result
    ///     A shared pointer to the watchpoint.  May contain a NULL
    ///     pointer if the watchpoint doesn't exist.
    //------------------------------------------------------------------
    const lldb::WatchpointSP
    FindByAddress (lldb::addr_t addr) const;

    //------------------------------------------------------------------
    /// Returns a shared pointer to the watchpoint with watchpoint spec
    /// \a spec -
    /// const version.
    ///
    /// @param[in] spec
    ///     The watchpoint spec to look for.
    ///
    /// @result
    ///     A shared pointer to the watchpoint.  May contain a NULL
    ///     pointer if the watchpoint doesn't exist.
    //------------------------------------------------------------------
    const lldb::WatchpointSP
    FindBySpec (std::string spec) const;

    //------------------------------------------------------------------
    /// Returns a shared pointer to the watchpoint with id
    /// \a watchID, const
    /// version.
    ///
    /// @param[in] watchID
    ///     The watchpoint location ID to seek for.
    ///
    /// @result
    ///     A shared pointer to the watchpoint.  May contain a NULL
    ///     pointer if the watchpoint doesn't exist.
    //------------------------------------------------------------------
    lldb::WatchpointSP
    FindByID (lldb::watch_id_t watchID) const;

    //------------------------------------------------------------------
    /// Returns the watchpoint id to the watchpoint
    /// at address \a addr.
    ///
    /// @param[in] addr
    ///     The address to match.
    ///
    /// @result
    ///     The ID of the watchpoint, or LLDB_INVALID_WATCH_ID.
    //------------------------------------------------------------------
    lldb::watch_id_t
    FindIDByAddress (lldb::addr_t addr);

    //------------------------------------------------------------------
    /// Returns the watchpoint id to the watchpoint
    /// with watchpoint spec \a spec.
    ///
    /// @param[in] spec
    ///     The watchpoint spec to match.
    ///
    /// @result
    ///     The ID of the watchpoint, or LLDB_INVALID_WATCH_ID.
    //------------------------------------------------------------------
    lldb::watch_id_t
    FindIDBySpec (std::string spec);

    //------------------------------------------------------------------
    /// Returns a shared pointer to the watchpoint with index \a i.
    ///
    /// @param[in] i
    ///     The watchpoint index to seek for.
    ///
    /// @result
    ///     A shared pointer to the watchpoint.  May contain a NULL pointer if
    ///     the watchpoint doesn't exist.
    //------------------------------------------------------------------
    lldb::WatchpointSP
    GetByIndex (uint32_t i);

    //------------------------------------------------------------------
    /// Returns a shared pointer to the watchpoint with index \a i, const
    /// version.
    ///
    /// @param[in] i
    ///     The watchpoint index to seek for.
    ///
    /// @result
    ///     A shared pointer to the watchpoint.  May contain a NULL pointer if
    ///     the watchpoint location doesn't exist.
    //------------------------------------------------------------------
    const lldb::WatchpointSP
    GetByIndex (uint32_t i) const;

    //------------------------------------------------------------------
    /// Removes the watchpoint given by \b watchID from this list.
    ///
    /// @param[in] watchID
    ///   The watchpoint ID to remove.
    ///
    /// @result
    ///   \b true if the watchpoint \a watchID was in the list.
    //------------------------------------------------------------------
    bool
    Remove (lldb::watch_id_t watchID);

    //------------------------------------------------------------------
    /// Returns the number hit count of all watchpoints in this list.
    ///
    /// @result
    ///     Hit count of all watchpoints in this list.
    //------------------------------------------------------------------
    uint32_t
    GetHitCount () const;

    //------------------------------------------------------------------
    /// Enquires of the watchpoint in this list with ID \a watchID whether we
    /// should stop.
    ///
    /// @param[in] context
    ///     This contains the information about this stop.
    ///
    /// @param[in] watchID
    ///     This watch ID that we hit.
    ///
    /// @return
    ///     \b true if we should stop, \b false otherwise.
    //------------------------------------------------------------------
    bool
    ShouldStop (StoppointCallbackContext *context,
                lldb::watch_id_t watchID);

    //------------------------------------------------------------------
    /// Returns the number of elements in this watchpoint list.
    ///
    /// @result
    ///     The number of elements.
    //------------------------------------------------------------------
    size_t
    GetSize() const
    {
        Mutex::Locker locker(m_mutex);
        return m_watchpoints.size();
    }

    //------------------------------------------------------------------
    /// Print a description of the watchpoints in this list to the stream \a s.
    ///
    /// @param[in] s
    ///     The stream to which to print the description.
    ///
    /// @param[in] level
    ///     The description level that indicates the detail level to
    ///     provide.
    ///
    /// @see lldb::DescriptionLevel
    //------------------------------------------------------------------
    void
    GetDescription (Stream *s,
                    lldb::DescriptionLevel level);

    void
    SetEnabledAll (bool enabled);

    void
    RemoveAll ();
    
    //------------------------------------------------------------------
    /// Sets the passed in Locker to hold the Watchpoint List mutex.
    ///
    /// @param[in] locker
    ///   The locker object that is set.
    //------------------------------------------------------------------
    void
    GetListMutex (lldb_private::Mutex::Locker &locker);

protected:
    typedef std::list<lldb::WatchpointSP> wp_collection;
    typedef std::vector<lldb::watch_id_t> id_vector;

    id_vector
    GetWatchpointIDs() const;

    wp_collection::iterator
    GetIDIterator(lldb::watch_id_t watchID);

    wp_collection::const_iterator
    GetIDConstIterator(lldb::watch_id_t watchID) const;

    wp_collection m_watchpoints;
    mutable Mutex m_mutex;

    lldb::watch_id_t m_next_wp_id;
};

} // namespace lldb_private

#endif  // liblldb_WatchpointList_h_
