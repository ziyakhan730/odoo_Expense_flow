import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  LayoutDashboard, 
  Upload, 
  History, 
  User,
  DollarSign,
  Clock,
  CheckCircle2,
  XCircle,
  RefreshCw
} from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Routes, Route } from "react-router-dom";
import ExpenseSubmission from "./ExpenseSubmission";
import EmployeeExpenses from "./EmployeeExpenses";
import { apiService } from "../services/api";
import { toast } from "sonner";

const navItems = [
  { label: "Dashboard", path: "/employee", icon: LayoutDashboard },
  { label: "Submit Expense", path: "/employee/submit", icon: Upload },
  { label: "History", path: "/employee/history", icon: History },
  { label: "Profile", path: "/employee/profile", icon: User },
];

interface DashboardData {
  total_submitted: number;
  pending_amount: number;
  approved_amount: number;
  rejected_amount: number;
  pending_count: number;
  approved_count: number;
  rejected_count: number;
  recent_expenses: Array<{
    id: number;
    title: string;
    description: string;
    amount: number;
    currency: string;
    status: string;
    category: {
      name: string;
    };
    expense_date: string;
    submission_date: string;
  }>;
  total_expenses: number;
}

const EmployeeOverview = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getEmployeeDashboardData();
      setDashboardData(data);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      setError(err.message || 'Failed to load dashboard data');
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      approved: "success" as const,
      rejected: "destructive" as const,
      pending: "warning" as const,
      in_progress: "secondary" as const,
    };
    return <Badge variant={variants[status as keyof typeof variants]}>{status}</Badge>;
  };

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

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

  const stats = dashboardData ? [
    { label: "Total Submitted", value: formatCurrency(dashboardData.total_submitted), icon: DollarSign, color: "text-primary" },
    { label: "Pending", value: formatCurrency(dashboardData.pending_amount), icon: Clock, color: "text-warning" },
    { label: "Approved", value: formatCurrency(dashboardData.approved_amount), icon: CheckCircle2, color: "text-success" },
    { label: "Rejected", value: formatCurrency(dashboardData.rejected_amount), icon: XCircle, color: "text-destructive" },
  ] : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Employee Dashboard</h1>
          <p className="text-muted-foreground">Manage your expense claims</p>
        </div>
        <Button onClick={loadDashboardData} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
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


        {/* Expense History */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Expenses</CardTitle>
            <CardDescription>Your latest expense submissions</CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData?.recent_expenses && dashboardData.recent_expenses.length > 0 ? (
              <div className="space-y-4">
                {dashboardData.recent_expenses.map((expense) => (
                  <div
                    key={expense.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                  >
                    <div className="space-y-1">
                      <p className="font-medium">{expense.title}</p>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span>{expense.category?.name || 'Uncategorized'}</span>
                        <span>•</span>
                        <span>{formatDate(expense.expense_date)}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="font-bold">
                          {formatCurrency(expense.amount, expense.currency)}
                        </p>
                      </div>
                      {getStatusBadge(expense.status)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">No expenses submitted yet.</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Submit your first expense to see it here.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
    </div>
  );
};

const EmployeeDashboard = () => {
  return (
    <DashboardLayout role="employee" navItems={navItems}>
      <Routes>
        <Route path="/" element={<EmployeeOverview />} />
        <Route path="/submit" element={<ExpenseSubmission />} />
        <Route path="/history" element={<EmployeeExpenses />} />
        <Route path="/profile" element={<div>Profile - Coming Soon</div>} />
      </Routes>
    </DashboardLayout>
  );
};

export default EmployeeDashboard;
