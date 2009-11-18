// Copyright (C) 2006-2009 Rosen Diankov (rdiankov@cs.cmu.edu)
//
// This file is part of OpenRAVE.
// OpenRAVE is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
#ifndef OPENRAVE_INTERFACE_BASE
#define OPENRAVE_INTERFACE_BASE

namespace OpenRAVE {

/// base class for all interfaces that OpenRAVE provides
class InterfaceBase : public boost::enable_shared_from_this<InterfaceBase>
{
public:
    typedef std::map<std::string, XMLReadablePtr, CaseInsentiveCompare> READERSMAP;

    InterfaceBase(PluginType type, EnvironmentBasePtr penv) : __type(type), __penv(penv) {}
	virtual ~InterfaceBase() {}

    inline PluginType GetInterfaceType() const { return __type; }

    /// set internally by RaveDatabase
	/// \return the unique identifier that describes this class type, case is ignored
    /// should be the same id used to create the object
    inline const std::string& GetXMLId() const { return __strxmlid; }

    /// set internally by RaveDatabase
    /// \return the pluginname this interface was loaded from
    inline const std::string& GetPluginName() const { return __strpluginname; }

    /// \return the environment that this interface is attached to
    inline EnvironmentBasePtr GetEnv() const { return __penv; }

    inline const READERSMAP& GetReadableInterfaces() const { return __mapReadableInterfaces; }
    inline XMLReadablePtr GetReadableInterface(const std::string& xmltag) const
    {
        READERSMAP::const_iterator it = __mapReadableInterfaces.find(xmltag);
        return it != __mapReadableInterfaces.end() ? it->second : XMLReadablePtr();
    }

    virtual const std::string& GetDescription() const { return __description; };

    virtual void SetUserData(boost::shared_ptr<void> pdata) { __pUserData = pdata; }
    virtual boost::shared_ptr<void> GetUserData() const { return __pUserData; }
    
    /// clone the contents of an interface to the current interface
    /// \param preference the interface whose information to clone
    /// \param cloningoptions mask of CloningOptions
    virtual bool Clone(InterfaceBaseConstPtr preference, int cloningoptions);

    /// Used to send special commands to the interface
    /// If the command is not supported, will throw an openrave_exception
    /// \param is the input stream containing the command
    /// \param os the output stream containing the output
    /// \return true if the command is successfully processed, otherwise false
    virtual bool SendCommand(std::ostream& os, std::istream& is) { throw openrave_exception("not commands supported",ORE_CommandNotSupported); }

protected:
    virtual const char* GetHash() const = 0;
    std::string __description;

private:
    boost::shared_ptr<void> __plugin; ///< handle to plugin that controls the executable code. As long as this plugin pointer is present, module will not be unloaded.
    std::string __strpluginname, __strxmlid;
    PluginType __type;
    EnvironmentBasePtr __penv;
    boost::shared_ptr<void> __pUserData;                       ///< data set by the user

    READERSMAP __mapReadableInterfaces; ///< pointers to extra interfaces that are included with this object

#ifdef RAVE_PRIVATE
#ifdef _MSC_VER
    friend class RaveDatabase;
    friend class Environment;
    friend class OpenRAVEXMLParser;
#else
    friend class ::RaveDatabase;
    friend class ::Environment;
    friend class ::OpenRAVEXMLParser;
#endif
#endif
};

} // end namespace OpenRAVE

#endif
