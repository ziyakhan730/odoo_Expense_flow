import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { 
  LayoutDashboard, 
  CheckCircle, 
  XCircle, 
  Users,
  Clock,
  DollarSign,
  TrendingUp
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Dashboard", path: "/manager", icon: LayoutDashboard },
  { label: "Pending Approvals", path: "/manager/pending", icon: Clock },
  { label: "Approved", path: "/manager/approved", icon: CheckCircle },
  { label: "Team Overview", path: "/manager/team", icon: Users },
];

const mockPendingExpenses = [
  { 
    id: 1, 
    employee: "Sarah Johnson", 
    amount: 1200, 
    currency: "USD", 
    category: "Hotel", 
    date: "2024-01-14", 
    description: "Conference accommodation",
    converted: 1200
  },
  { 
    id: 2, 
    employee: "Mike Chen", 
    amount: 850, 
    currency: "EUR", 
    category: "Travel", 
    date: "2024-01-13", 
    description: "Flight to Berlin",
    converted: 925
  },
  { 
    id: 3, 
    employee: "Emma Davis", 
    amount: 320, 
    currency: "GBP", 
    category: "Meals", 
    date: "2024-01-12", 
    description: "Client dinner",
    converted: 405
  },
];

const ManagerDashboard = () => {
  const [selectedExpense, setSelectedExpense] = useState<typeof mockPendingExpenses[0] | null>(null);
  const [actionType, setActionType] = useState<"approve" | "reject" | null>(null);

  const handleAction = (action: "approve" | "reject") => {
    toast.success(`Expense ${action}d successfully!`);
    setSelectedExpense(null);
    setActionType(null);
  };

  const stats = [
    { label: "Pending Approvals", value: "3", icon: Clock, color: "text-warning" },
    { label: "Approved This Month", value: "24", icon: CheckCircle, color: "text-success" },
    { label: "Total Amount", value: "$18,450", icon: DollarSign, color: "text-primary" },
    { label: "Avg Processing Time", value: "2.3 days", icon: TrendingUp, color: "text-secondary" },
  ];

  return (
    <DashboardLayout role="manager" navItems={navItems}>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Manager Dashboard</h1>
          <p className="text-muted-foreground">Review and approve team expenses</p>
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
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Pending Approvals */}
        <Card>
          <CardHeader>
            <CardTitle>Pending Approvals</CardTitle>
            <CardDescription>Review and action expense claims</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockPendingExpenses.map((expense) => (
                <div
                  key={expense.id}
                  className="flex items-center justify-between p-4 rounded-lg border-2 border-border hover:border-primary/50 transition-colors"
                >
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold">{expense.employee}</p>
                      <Badge variant="pending">{expense.category}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{expense.description}</p>
                    <p className="text-xs text-muted-foreground">{expense.date}</p>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right mr-4">
                      <p className="font-bold text-lg">
                        {expense.amount} {expense.currency}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        ≈ ${expense.converted} USD
                      </p>
                    </div>

                    <div className="flex gap-2">
                      <Dialog open={selectedExpense?.id === expense.id && actionType === "reject"} onOpenChange={(open) => !open && setSelectedExpense(null)}>
                        <DialogTrigger asChild>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedExpense(expense);
                              setActionType("reject");
                            }}
                          >
                            <XCircle className="h-4 w-4 mr-2" />
                            Reject
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Reject Expense</DialogTitle>
                            <DialogDescription>
                              Please provide a reason for rejecting this expense claim.
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <Textarea placeholder="Reason for rejection..." />
                            <div className="flex gap-2 justify-end">
                              <Button variant="outline" onClick={() => setSelectedExpense(null)}>
                                Cancel
                              </Button>
                              <Button variant="destructive" onClick={() => handleAction("reject")}>
                                Confirm Rejection
                              </Button>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>

                      <Dialog open={selectedExpense?.id === expense.id && actionType === "approve"} onOpenChange={(open) => !open && setSelectedExpense(null)}>
                        <DialogTrigger asChild>
                          <Button
                            size="sm"
                            onClick={() => {
                              setSelectedExpense(expense);
                              setActionType("approve");
                            }}
                          >
                            <CheckCircle className="h-4 w-4 mr-2" />
                            Approve
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Approve Expense</DialogTitle>
                            <DialogDescription>
                              Confirm approval of this expense claim
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div className="p-4 bg-muted rounded-lg space-y-2">
                              <p><span className="font-semibold">Employee:</span> {expense.employee}</p>
                              <p><span className="font-semibold">Amount:</span> {expense.amount} {expense.currency}</p>
                              <p><span className="font-semibold">Category:</span> {expense.category}</p>
                              <p><span className="font-semibold">Description:</span> {expense.description}</p>
                            </div>
                            <Textarea placeholder="Add a comment (optional)..." />
                            <div className="flex gap-2 justify-end">
                              <Button variant="outline" onClick={() => setSelectedExpense(null)}>
                                Cancel
                              </Button>
                              <Button onClick={() => handleAction("approve")}>
                                Confirm Approval
                              </Button>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Approval Timeline */}
        <Card>
          <CardHeader>
            <CardTitle>Approval Progress</CardTitle>
            <CardDescription>Track expense workflow stages</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-success text-success-foreground">
                  <CheckCircle className="h-5 w-5" />
                </div>
                <div className="flex-1">
                  <p className="font-medium">Submitted</p>
                  <p className="text-sm text-muted-foreground">Employee submitted expense claim</p>
                </div>
              </div>
              <div className="ml-5 h-8 w-px bg-border" />
              <div className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-warning text-warning-foreground">
                  <Clock className="h-5 w-5" />
                </div>
                <div className="flex-1">
                  <p className="font-medium">Manager Review</p>
                  <p className="text-sm text-muted-foreground">Awaiting your approval</p>
                </div>
              </div>
              <div className="ml-5 h-8 w-px bg-border opacity-30" />
              <div className="flex items-center gap-4 opacity-50">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted text-muted-foreground">
                  <DollarSign className="h-5 w-5" />
                </div>
                <div className="flex-1">
                  <p className="font-medium">Processing Payment</p>
                  <p className="text-sm text-muted-foreground">Finance team processing</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default ManagerDashboard;
