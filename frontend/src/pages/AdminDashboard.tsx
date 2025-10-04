import { Routes, Route } from "react-router-dom";
import DashboardLayout from "@/components/layout/DashboardLayout";
import UserManagement from "./UserManagement";
import AdminOverview from "./AdminOverview";
import { 
  LayoutDashboard, 
  Users, 
  Settings,
  BarChart3
} from "lucide-react";

const navItems = [
  { label: "Overview", path: "/admin", icon: LayoutDashboard },
  { label: "Users", path: "/admin/users", icon: Users },
  { label: "Rules", path: "/admin/rules", icon: Settings },
  { label: "Analytics", path: "/admin/analytics", icon: BarChart3 },
];

const AdminDashboard = () => {
  return (
    <DashboardLayout role="admin" navItems={navItems}>
      <Routes>
        <Route path="/" element={<AdminOverview />} />
        <Route path="/users" element={<UserManagement />} />
        <Route path="/rules" element={<div>Rules Management - Coming Soon</div>} />
        <Route path="/analytics" element={<div>Analytics - Coming Soon</div>} />
      </Routes>
    </DashboardLayout>
  );
};

export default AdminDashboard;
