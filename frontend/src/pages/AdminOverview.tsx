import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { 
  Plus,
  UserPlus,
  Trash2,
  DollarSign,
  TrendingUp,
  FileText,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  Eye
} from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { apiService } from "../services/api";

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  phone?: string;
  user_set?: number;
  company: number;
  created_at: string;
}

const mockRules = [
  { id: 1, condition: "Amount > $5,000", action: "Require CFO approval" },
  { id: 2, condition: "Category = Travel", action: "Require manager + HR approval" },
  { id: 3, condition: "Amount > $10,000", action: "Require board approval" },
];

interface DashboardData {
  total_users: number;
  monthly_expenses: number;
  pending_approvals: number;
  avg_processing_time: number;
  approval_rate: number;
  rejection_rate: number;
  total_processed: number;
  expenses_by_category: Array<{
    category: string;
    amount: number;
    percentage: number;
    count: number;
  }>;
  user_growth: number;
  expense_growth: number;
  approval_change: number;
  processing_change: number;
  recent_users: number;
  total_expenses_count: number;
  rejected_amount: number;
}

const AdminOverview = () => {
  const [showAddUser, setShowAddUser] = useState(false);
  const [showAddRule, setShowAddRule] = useState(false);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [usersLoading, setUsersLoading] = useState(false);

  const handleAddUser = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("User added successfully!");
    setShowAddUser(false);
  };

  const handleAddRule = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("Rule created successfully!");
    setShowAddRule(false);
  };

  useEffect(() => {
    loadDashboardData();
    loadUsers();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getAdminDashboardData();
      setDashboardData(data);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      setUsersLoading(true);
      console.log('Loading users...');
      console.log('API Service authenticated:', apiService.isAuthenticated());
      
      // Check if user is authenticated
      if (!apiService.isAuthenticated()) {
        console.error('User not authenticated');
        toast.error('Please log in to view users');
        setUsers([]);
        return;
      }
      
      const usersData = await apiService.getUsers();
      console.log('Users data received:', usersData);
      console.log('Users data type:', typeof usersData);
      
      // Handle paginated response
      let usersList = [];
      if (Array.isArray(usersData)) {
        usersList = usersData;
        console.log('Users data is array, length:', usersList.length);
      } else if (usersData && usersData.results) {
        usersList = usersData.results;
        console.log('Users data has results, length:', usersList.length);
      } else if (usersData && usersData.data) {
        usersList = usersData.data;
        console.log('Users data has data, length:', usersList.length);
      } else {
        console.log('Users data format not recognized:', usersData);
      }
      
      console.log('Processed users list:', usersList);
      console.log('Setting users with count:', usersList.length);
      setUsers(usersList);
    } catch (err: any) {
      console.error('Error loading users:', err);
      console.error('Error details:', {
        message: err.message,
        stack: err.stack,
        name: err.name
      });
      toast.error('Failed to load users: ' + err.message);
      setUsers([]);
    } finally {
      setUsersLoading(false);
    }
  };

  const stats = dashboardData ? [
    { 
      label: "Total Users", 
      value: dashboardData.total_users.toString(), 
      icon: Users, 
      color: "text-primary", 
      change: `+${dashboardData.user_growth}%` 
    },
    { 
      label: "Monthly Expenses", 
      value: `$${dashboardData.monthly_expenses.toLocaleString()}`, 
      icon: DollarSign, 
      color: "text-success", 
      change: `+${dashboardData.expense_growth}%`,
      subtitle: "Excludes rejected bills"
    },
    { 
      label: "Pending Approvals", 
      value: dashboardData.pending_approvals.toString(), 
      icon: FileText, 
      color: "text-warning", 
      change: `${dashboardData.approval_change}%` 
    },
    { 
      label: "Avg Processing Time", 
      value: `${dashboardData.avg_processing_time} days`, 
      icon: Clock, 
      color: "text-secondary", 
      change: `${dashboardData.processing_change}%` 
    },
  ] : [];

  const expensesByCategory = dashboardData?.expenses_by_category || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={loadDashboardData}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground">Manage users, rules, and view analytics</p>
        </div>
        <button 
          onClick={loadDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Refresh Data
        </button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
                <Icon className={cn("h-4 w-4", stat.color)} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  <span className={stat.change.startsWith("+") ? "text-success" : "text-destructive"}>
                    {stat.change}
                  </span> from last month
                </p>
                {stat.subtitle && (
                  <p className="text-xs text-muted-foreground mt-1 italic">
                    {stat.subtitle}
                  </p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Charts */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Expenses by Category</CardTitle>
            <CardDescription>Monthly breakdown (excludes rejected bills)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {expensesByCategory.map((item) => (
              <div key={item.category} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{item.category}</span>
                  <span className="text-muted-foreground">${item.amount.toLocaleString()}</span>
                </div>
                <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary transition-all duration-500"
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
                <p className="text-xs text-muted-foreground">{item.percentage}% of total</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Approval Metrics</CardTitle>
            <CardDescription>Last 30 days</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Approval Rate</span>
                <span className="text-2xl font-bold text-success">{dashboardData?.approval_rate || 0}%</span>
              </div>
              <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-success transition-all duration-500" 
                  style={{ width: `${dashboardData?.approval_rate || 0}%` }} 
                />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Rejection Rate</span>
                <span className="text-2xl font-bold text-destructive">{dashboardData?.rejection_rate || 0}%</span>
              </div>
              <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-destructive transition-all duration-500" 
                  style={{ width: `${dashboardData?.rejection_rate || 0}%` }} 
                />
              </div>
            </div>
            <div className="pt-4 border-t">
              <p className="text-sm text-muted-foreground">
                <span className="font-semibold text-foreground">{dashboardData?.total_processed || 0}</span> expenses processed this month
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* User Management */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>User Management</CardTitle>
            <CardDescription>Manage employee and manager accounts</CardDescription>
          </div>
          <Dialog open={showAddUser} onOpenChange={setShowAddUser}>
            <DialogTrigger asChild>
              <Button>
                <UserPlus className="h-4 w-4 mr-2" />
                Add User
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New User</DialogTitle>
                <DialogDescription>Create a new user account</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleAddUser} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="user-name">Full Name</Label>
                  <Input id="user-name" placeholder="John Doe" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="user-email">Email</Label>
                  <Input id="user-email" type="email" placeholder="john@company.com" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="user-role">Role</Label>
                  <Select required>
                    <SelectTrigger id="user-role">
                      <SelectValue placeholder="Select role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="employee">Employee</SelectItem>
                      <SelectItem value="manager">Manager</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="user-dept">Department</Label>
                  <Input id="user-dept" placeholder="Engineering" required />
                </div>
                <Button type="submit" className="w-full">Create User</Button>
              </form>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent>
          {usersLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="ml-2">Loading users...</span>
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-8">
              <Users className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No Users Found</h3>
              <p className="text-muted-foreground">No users have been created yet.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {users.map((user) => (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors cursor-pointer"
                  onClick={() => setSelectedUser(user)}
                >
                  <div className="space-y-1">
                    <p className="font-medium">{user.first_name} {user.last_name}</p>
                    <p className="text-sm text-muted-foreground">{user.email}</p>
                    <p className="text-xs text-muted-foreground">@{user.username}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <Badge variant={user.role === "admin" ? "destructive" : user.role === "manager" ? "secondary" : "default"}>
                      {user.role.toUpperCase()}
                    </Badge>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedUser(user);
                      }}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Approval Rules */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Approval Rules</CardTitle>
            <CardDescription>Define conditional approval workflows</CardDescription>
          </div>
          <Dialog open={showAddRule} onOpenChange={setShowAddRule}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                Add Rule
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Approval Rule</DialogTitle>
                <DialogDescription>Set conditions and required approvers</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleAddRule} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="rule-condition">Condition Type</Label>
                  <Select required>
                    <SelectTrigger id="rule-condition">
                      <SelectValue placeholder="Select condition" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="amount">Amount</SelectItem>
                      <SelectItem value="category">Category</SelectItem>
                      <SelectItem value="department">Department</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="rule-value">Value</Label>
                  <Input id="rule-value" placeholder="e.g., > 5000 or Travel" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="rule-action">Required Approver</Label>
                  <Select required>
                    <SelectTrigger id="rule-action">
                      <SelectValue placeholder="Select approver" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="manager">Manager</SelectItem>
                      <SelectItem value="cfo">CFO</SelectItem>
                      <SelectItem value="hr">HR</SelectItem>
                      <SelectItem value="board">Board</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button type="submit" className="w-full">Create Rule</Button>
              </form>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockRules.map((rule) => (
              <div
                key={rule.id}
                className="flex items-center justify-between p-4 rounded-lg border-2 border-border"
              >
                <div className="flex-1">
                  <p className="font-medium text-sm">
                    <span className="text-primary">IF</span> {rule.condition}
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    <span className="text-secondary">THEN</span> {rule.action}
                  </p>
                </div>
                <Button variant="ghost" size="icon">
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* User Details Dialog */}
      <Dialog open={!!selectedUser} onOpenChange={() => setSelectedUser(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              User Details
            </DialogTitle>
            <DialogDescription>
              Complete information about the selected user
            </DialogDescription>
          </DialogHeader>
          {selectedUser && (
            <div className="space-y-6">
              {/* User Basic Info */}
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Full Name</label>
                    <p className="text-lg font-semibold">{selectedUser.first_name} {selectedUser.last_name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Username</label>
                    <p className="text-sm">@{selectedUser.username}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Email</label>
                    <p className="text-sm">{selectedUser.email}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Phone</label>
                    <p className="text-sm">{selectedUser.phone || 'Not provided'}</p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Role</label>
                    <div className="mt-1">
                      <Badge variant={selectedUser.role === "admin" ? "destructive" : selectedUser.role === "manager" ? "secondary" : "default"}>
                        {selectedUser.role.toUpperCase()}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">User ID</label>
                    <p className="text-sm font-mono">#{selectedUser.id}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">User Set</label>
                    <p className="text-sm">{selectedUser.user_set ? `Set #${selectedUser.user_set}` : 'Not assigned'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Company ID</label>
                    <p className="text-sm font-mono">#{selectedUser.company}</p>
                  </div>
                </div>
              </div>

              {/* Account Information */}
              <div className="border-t pt-6">
                <h4 className="font-semibold mb-4">Account Information</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Created At</label>
                    <p className="text-sm">{new Date(selectedUser.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Account Status</label>
                    <p className="text-sm text-green-600 font-medium">Active</p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="border-t pt-6 flex justify-end gap-2">
                <Button variant="outline" onClick={() => setSelectedUser(null)}>
                  Close
                </Button>
                <Button variant="destructive" size="sm">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete User
                </Button>
                <Button size="sm">
                  <UserPlus className="h-4 w-4 mr-2" />
                  Edit User
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminOverview;
