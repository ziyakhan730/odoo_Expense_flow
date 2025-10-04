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
  FileText
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const mockUsers = [
  { id: 1, name: "Sarah Johnson", email: "sarah@company.com", role: "employee", department: "Marketing" },
  { id: 2, name: "Mike Chen", email: "mike@company.com", role: "manager", department: "Engineering" },
  { id: 3, name: "Emma Davis", email: "emma@company.com", role: "employee", department: "Sales" },
];

const mockRules = [
  { id: 1, condition: "Amount > $5,000", action: "Require CFO approval" },
  { id: 2, condition: "Category = Travel", action: "Require manager + HR approval" },
  { id: 3, condition: "Amount > $10,000", action: "Require board approval" },
];

const AdminOverview = () => {
  const [showAddUser, setShowAddUser] = useState(false);
  const [showAddRule, setShowAddRule] = useState(false);

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

  const stats = [
    { label: "Total Users", value: "147", icon: DollarSign, color: "text-primary", change: "+12%" },
    { label: "Monthly Expenses", value: "$84,350", icon: DollarSign, color: "text-success", change: "+8.2%" },
    { label: "Pending Approvals", value: "23", icon: FileText, color: "text-warning", change: "-15%" },
    { label: "Avg Processing Time", value: "1.8 days", icon: TrendingUp, color: "text-secondary", change: "-22%" },
  ];

  const expensesByCategory = [
    { category: "Travel", amount: 32450, percentage: 38 },
    { category: "Hotel", amount: 25300, percentage: 30 },
    { category: "Meals", amount: 16870, percentage: 20 },
    { category: "Office", amount: 10130, percentage: 12 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground">Manage users, rules, and view analytics</p>
        </div>
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
            <CardDescription>Monthly breakdown</CardDescription>
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
                <span className="text-2xl font-bold text-success">94%</span>
              </div>
              <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-success w-[94%]" />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Rejection Rate</span>
                <span className="text-2xl font-bold text-destructive">6%</span>
              </div>
              <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-destructive w-[6%]" />
              </div>
            </div>
            <div className="pt-4 border-t">
              <p className="text-sm text-muted-foreground">
                <span className="font-semibold text-foreground">842</span> expenses processed this month
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
          <div className="space-y-4">
            {mockUsers.map((user) => (
              <div
                key={user.id}
                className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors"
              >
                <div className="space-y-1">
                  <p className="font-medium">{user.name}</p>
                  <p className="text-sm text-muted-foreground">{user.email}</p>
                  <p className="text-xs text-muted-foreground">{user.department}</p>
                </div>
                <div className="flex items-center gap-4">
                  <Badge variant={user.role === "admin" ? "destructive" : user.role === "manager" ? "secondary" : "default"}>
                    {user.role}
                  </Badge>
                  <Button variant="ghost" size="icon">
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
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
    </div>
  );
};

export default AdminOverview;
