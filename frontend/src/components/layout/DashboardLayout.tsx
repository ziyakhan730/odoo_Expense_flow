import { ReactNode, useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Bell, LogOut, Menu, User, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { apiService } from "@/services/api";
import { toast } from "sonner";

interface DashboardLayoutProps {
  children: ReactNode;
  role: "admin" | "manager" | "employee";
  navItems: Array<{
    label: string;
    path: string;
    icon: React.ComponentType<{ className?: string }>;
  }>;
}

const DashboardLayout = ({ children, role, navItems }: DashboardLayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const saved = localStorage.getItem('sidebar-collapsed');
    return saved ? JSON.parse(saved) : false;
  });

  // Save sidebar state to localStorage
  useEffect(() => {
    localStorage.setItem('sidebar-collapsed', JSON.stringify(sidebarCollapsed));
  }, [sidebarCollapsed]);

  // Keyboard shortcut for toggling sidebar
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'b') {
        event.preventDefault();
        setSidebarCollapsed(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleLogout = async () => {
    try {
      await apiService.logout();
      toast.success("Logged out successfully!");
      navigate("/auth");
    } catch (error: any) {
      toast.error("Logout failed. Please try again.");
      console.error('Logout error:', error);
      // Even if logout fails, clear local storage and redirect
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      navigate("/auth");
    }
  };

  const getRoleBadge = () => {
    const variants = {
      admin: "destructive" as const,
      manager: "secondary" as const,
      employee: "default" as const,
    };
    return <Badge variant={variants[role]}>{role.toUpperCase()}</Badge>;
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="header-container">
          <div className="header-content h-16 px-4 sm:px-6 lg:px-8">
            <div className="header-left">
              <div className="flex items-center gap-4">
                <Link to="/" className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-lg bg-gradient-hero" />
                  <span className="logo-text">ExpenseFlow</span>
                </Link>
                {getRoleBadge()}
              </div>
            </div>

            <div className="header-right">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                      className="h-9 w-9"
                    >
                      {sidebarCollapsed ? (
                        <ChevronRight className="h-4 w-4" />
                      ) : (
                        <ChevronLeft className="h-4 w-4" />
                      )}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'} (Ctrl+B)</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
              
              <Button variant="ghost" size="icon" className="relative h-9 w-9">
                <Bell className="h-4 w-4 sm:h-5 sm:w-5" />
                <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-destructive" />
              </Button>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                    <Avatar>
                      <AvatarFallback className="bg-primary text-primary-foreground">
                        <User className="h-5 w-5" />
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end">
                  <DropdownMenuLabel>My Account</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="text-destructive" onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={cn(
          "sticky top-16 hidden h-[calc(100vh-4rem)] flex-col border-r border-border bg-muted/30 transition-all duration-300 lg:flex",
          sidebarCollapsed ? "w-16" : "w-64",
          sidebarCollapsed && "sidebar-collapsed"
        )}>
          <nav className="flex-1 space-y-1 p-3 sm:p-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              const linkContent = (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    "nav-item flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                    sidebarCollapsed && "justify-center px-2"
                  )}
                >
                  <Icon className={cn("h-4 w-4 flex-shrink-0", sidebarCollapsed && "icon")} />
                  {!sidebarCollapsed && (
                    <span className="truncate">{item.label}</span>
                  )}
                </Link>
              );

              if (sidebarCollapsed) {
                return (
                  <TooltipProvider key={item.path}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        {linkContent}
                      </TooltipTrigger>
                      <TooltipContent side="right">
                        <p>{item.label}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                );
              }

              return linkContent;
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
