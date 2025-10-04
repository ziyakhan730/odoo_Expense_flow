import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Plus, Users, UserCheck, UserX, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { apiService } from "@/services/api";

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  user_set: number | null;
  company: number;
}

interface UserSet {
  id: number;
  name: string;
  manager: number | null;
  manager_name: string;
  manager_email: string;
  employees_count: number;
  employees: User[];
}

const UserManagement = () => {
  const navigate = useNavigate();
  const [userSets, setUserSets] = useState<UserSet[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [availableManagers, setAvailableManagers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateSet, setShowCreateSet] = useState(false);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [selectedSet, setSelectedSet] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [newSetName, setNewSetName] = useState("");
  const [newUserData, setNewUserData] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    role: "employee",
    set_id: "",
    phone: ""
  });

  useEffect(() => {
    // Check if user is authenticated
    if (!apiService.isAuthenticated()) {
      setError("You must be logged in to access user management");
      setLoading(false);
      toast.error("Please log in to access user management");
      navigate("/auth");
      return;
    }
    
    loadData();
  }, [navigate]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Loading user management data...');
      
      const [setsData, usersData, managersData] = await Promise.all([
        apiService.getUserSets(),
        apiService.getUsers(),
        apiService.getAvailableManagers()
      ]);
      
      console.log('API Response Data:', {
        setsData,
        usersData,
        managersData
      });
      
      console.log('Sets data type:', typeof setsData);
      console.log('Sets data structure:', setsData);
      if (setsData && setsData.results) {
        console.log('Found paginated results:', setsData.results);
      }
      
      // Handle paginated response for user sets
      const setsArray = setsData && setsData.results ? setsData.results : (Array.isArray(setsData) ? setsData : []);
      
      // Ensure data is arrays
      setUserSets(setsArray);
      setUsers(Array.isArray(usersData) ? usersData : []);
      setAvailableManagers(Array.isArray(managersData) ? managersData : []);
      
      console.log('Final sets array:', setsArray);
      console.log('Data loaded successfully');
    } catch (error: any) {
      console.error('Error loading data:', error);
      setError(error.message || "Failed to load data");
      toast.error(error.message || "Failed to load data");
      // Set empty arrays on error
      setUserSets([]);
      setUsers([]);
      setAvailableManagers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSet = async () => {
    try {
      await apiService.createUserSet({
        name: newSetName
      });
      
      toast.success("User set created successfully!");
      setShowCreateSet(false);
      setNewSetName("");
      loadData();
    } catch (error: any) {
      toast.error(error.message || "Failed to create user set");
    }
  };

  const handleCreateUser = async () => {
    try {
      // Validate required fields
      if (!newUserData.username || !newUserData.email || !newUserData.password || 
          !newUserData.first_name || !newUserData.last_name) {
        toast.error("Please fill in all required fields");
        return;
      }
      
      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(newUserData.email)) {
        toast.error("Please enter a valid email address");
        return;
      }
      
      // Validate password strength
      if (newUserData.password.length < 8) {
        toast.error("Password must be at least 8 characters long");
        return;
      }
      
      // Check for common passwords
      const commonPasswords = ['password', 'password123', '123456', '12345678', 'qwerty', 'abc123'];
      if (commonPasswords.includes(newUserData.password.toLowerCase())) {
        toast.error("Please choose a stronger password");
        return;
      }
      
      const userData = {
        username: newUserData.username,
        email: newUserData.email,
        first_name: newUserData.first_name,
        last_name: newUserData.last_name,
        password: newUserData.password,
        role: newUserData.role,
        phone: newUserData.phone || undefined
      };
      
      // Only add set_id if it's a valid number
      if (
        typeof newUserData.set_id !== "undefined" &&
        newUserData.set_id !== "" &&
        !isNaN(Number(newUserData.set_id))
      ) {
        // @ts-expect-error: set_id is not in the original userData type, but is accepted by the backend
        userData.set_id = Number(newUserData.set_id);
      }
 
      console.log('Creating user with data:', userData);
      await apiService.createUser(userData);
      
      toast.success("User created successfully!");
      setShowCreateUser(false);
      setNewUserData({
        username: "",
        email: "",
        first_name: "",
        last_name: "",
        password: "",
        role: "employee",
        set_id: "",
        phone: ""
      });
      loadData();
    } catch (error: any) {
      console.error('User creation error:', error);
      toast.error(error.message || "Failed to create user");
    }
  };

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      await apiService.updateUserRole(userId, newRole);
      toast.success("User role updated successfully!");
      loadData();
    } catch (error: any) {
      toast.error(error.message || "Failed to update user role");
    }
  };

  const handleSetChange = async (userId: number, newSetId: number) => {
    try {
      await apiService.updateUserSet(userId, newSetId);
      toast.success("User moved to new set successfully!");
      loadData();
    } catch (error: any) {
      toast.error(error.message || "Failed to move user");
    }
  };

  const handleAssignManager = async (setId: number, managerId: number) => {
    try {
      // This would need a new API endpoint to assign manager to set
      // For now, we'll use the existing user set update
      await apiService.updateUserSet(managerId, setId);
      toast.success("Manager assigned to set successfully!");
      loadData();
    } catch (error: any) {
      toast.error(error.message || "Failed to assign manager");
    }
  };

  const getRoleBadge = (role: string) => {
    const variants = {
      admin: "destructive" as const,
      manager: "secondary" as const,
      employee: "default" as const,
    };
    return <Badge variant={variants[role as keyof typeof variants]}>{role.toUpperCase()}</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading user management...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-lg text-red-600 mb-4">Error loading data</div>
          <div className="text-sm text-gray-600 mb-4">{error}</div>
          <Button onClick={loadData}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">User Management</h1>
          <p className="text-muted-foreground">Manage user sets, roles, and assignments</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={showCreateSet} onOpenChange={setShowCreateSet}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Set
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New User Set</DialogTitle>
                <DialogDescription>
                  Create a new user set. You can assign a manager later.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="set-name">Set Name</Label>
                  <Input
                    id="set-name"
                    value={newSetName}
                    onChange={(e) => setNewSetName(e.target.value)}
                    placeholder="Enter set name"
                  />
                </div>
                <Button onClick={handleCreateSet} disabled={!newSetName}>
                  Create Set
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={showCreateUser} onOpenChange={setShowCreateUser}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Users className="mr-2 h-4 w-4" />
                Add Employee
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New User</DialogTitle>
                <DialogDescription>
                  Create a new user and assign them to a set.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="first-name">First Name</Label>
                    <Input
                      id="first-name"
                      value={newUserData.first_name}
                      onChange={(e) => setNewUserData({...newUserData, first_name: e.target.value})}
                      placeholder="First name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="last-name">Last Name</Label>
                    <Input
                      id="last-name"
                      value={newUserData.last_name}
                      onChange={(e) => setNewUserData({...newUserData, last_name: e.target.value})}
                      placeholder="Last name"
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    value={newUserData.username}
                    onChange={(e) => setNewUserData({...newUserData, username: e.target.value})}
                    placeholder="Username"
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newUserData.email}
                    onChange={(e) => setNewUserData({...newUserData, email: e.target.value})}
                    placeholder="user@example.com"
                  />
                </div>
                <div>
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={newUserData.password}
                    onChange={(e) => setNewUserData({...newUserData, password: e.target.value})}
                    placeholder="At least 8 characters, avoid common passwords"
                  />
                </div>
                <div>
                  <Label htmlFor="set">Assign to Set (Optional)</Label>
                  <Select value={newUserData.set_id} onValueChange={(value) => setNewUserData({...newUserData, set_id: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a set (optional)" />
                    </SelectTrigger>
                    <SelectContent>
                      {Array.isArray(userSets) && userSets.map((set) => (
                        <SelectItem key={set.id} value={set.id.toString()}>
                          {set.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={handleCreateUser} disabled={!newUserData.username || !newUserData.email || !newUserData.password || !newUserData.first_name || !newUserData.last_name}>
                  Create User
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Debug Info */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mb-4 p-4 bg-gray-100 rounded-lg">
          <h4 className="font-semibold mb-2">Debug Info:</h4>
          <p>UserSets count: {Array.isArray(userSets) ? userSets.length : 'Not an array'}</p>
          <p>UserSets data: {JSON.stringify(userSets, null, 2)}</p>
        </div>
      )}

      {/* User Sets Display */}
      <div className="grid gap-6">
        {Array.isArray(userSets) && userSets.length > 0 && userSets.map((set) => (
          <Card key={set.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    {set.name}
                  </CardTitle>
                  <CardDescription>
                    {set.employees_count} employees
                  </CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedSet(selectedSet === set.id ? null : set.id)}
                >
                  {selectedSet === set.id ? "Hide" : "View"} Details
                  <ArrowRight className={`ml-2 h-4 w-4 transition-transform ${selectedSet === set.id ? 'rotate-90' : ''}`} />
                </Button>
              </div>
            </CardHeader>
            
              {/* Manager Section */}
              <CardContent>
                <div className="mb-4">
                  <h4 className="font-semibold text-sm text-muted-foreground mb-2">MANAGER</h4>
                  {set.manager ? (
                    <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
                      <UserCheck className="h-4 w-4 text-green-600" />
                      <div>
                        <div className="font-medium">{set.manager_name}</div>
                        <div className="text-sm text-muted-foreground">{set.manager_email}</div>
                      </div>
                      <Badge variant="secondary">MANAGER</Badge>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 p-3 bg-destructive/10 rounded-lg">
                        <UserX className="h-4 w-4 text-destructive" />
                        <div className="text-destructive">No manager assigned</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Select onValueChange={(managerId) => handleAssignManager(set.id, parseInt(managerId))}>
                          <SelectTrigger className="w-64">
                            <SelectValue placeholder="Assign a manager" />
                          </SelectTrigger>
                          <SelectContent>
                            {Array.isArray(availableManagers) && availableManagers.map((manager) => (
                              <SelectItem key={manager.id} value={manager.id.toString()}>
                                {manager.first_name} {manager.last_name} ({manager.email})
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  )}
                </div>

              {/* Employees Section */}
              {selectedSet === set.id && (
                <div>
                  <h4 className="font-semibold text-sm text-muted-foreground mb-2">EMPLOYEES</h4>
                  {set.employees.length > 0 ? (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name</TableHead>
                          <TableHead>Email</TableHead>
                          <TableHead>Role</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {Array.isArray(set.employees) && set.employees.map((employee) => (
                          <TableRow key={employee.id}>
                            <TableCell>{employee.first_name} {employee.last_name}</TableCell>
                            <TableCell>{employee.email}</TableCell>
                            <TableCell>{getRoleBadge(employee.role)}</TableCell>
                            <TableCell>
                              <div className="flex gap-2">
                                <Select
                                  value={employee.role}
                                  onValueChange={(value) => handleRoleChange(employee.id, value)}
                                >
                                  <SelectTrigger className="w-32">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="employee">Employee</SelectItem>
                                    <SelectItem value="manager">Manager</SelectItem>
                                  </SelectContent>
                                </Select>
                                
                                <Select
                                  value={employee.user_set?.toString() || ""}
                                  onValueChange={(value) => handleSetChange(employee.id, parseInt(value))}
                                >
                                  <SelectTrigger className="w-40">
                                    <SelectValue placeholder="Move to set" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {Array.isArray(userSets) && userSets.map((targetSet) => (
                                      <SelectItem key={targetSet.id} value={targetSet.id.toString()}>
                                        {targetSet.name}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  ) : (
                    <div className="text-center py-4 text-muted-foreground">
                      No employees in this set
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {Array.isArray(userSets) && userSets.length === 0 && !loading && (
        <Card>
          <CardContent className="text-center py-8">
            <Users className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">No User Sets</h3>
            <p className="text-muted-foreground mb-4">
              Create your first user set to start organizing your team.
            </p>
            <Button onClick={() => setShowCreateSet(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create First Set
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default UserManagement;
