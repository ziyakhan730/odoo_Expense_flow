import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { 
  FileText, 
  CheckCircle2, 
  BarChart3, 
  Scan, 
  Shield, 
  Globe,
  ArrowRight 
} from "lucide-react";
import { Link } from "react-router-dom";
import heroImage from "@/assets/hero-bg.jpg";
import ocrImage from "@/assets/feature-ocr.png";
import approvalImage from "@/assets/feature-approval.png";
import dashboardImage from "@/assets/feature-dashboard.png";

const Landing = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="header-container">
          <div className="header-content h-16 px-4 sm:px-6 lg:px-8">
            <div className="header-left">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-gradient-hero" />
                <span className="logo-text">ExpenseFlow</span>
              </div>
            </div>
            <nav className="hidden md:flex items-center gap-4 lg:gap-6">
              <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                Features
              </a>
              <a href="#pricing" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                Pricing
              </a>
              <Link to="/auth">
                <Button variant="ghost">Sign In</Button>
              </Link>
              <Link to="/company-registration">
                <Button variant="outline">Register Company</Button>
              </Link>
              <Link to="/auth">
                <Button>Get Started</Button>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 md:py-32 relative overflow-hidden">
        <div 
          className="absolute inset-0 opacity-10 bg-cover bg-center"
          style={{ backgroundImage: `url(${heroImage})` }}
        />
        <div className="absolute inset-0 bg-gradient-overlay" />
        <div className="container relative">
          <div className="mx-auto max-w-4xl text-center space-y-8 animate-fade-in">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              Automate Your Company's <br />
              <span className="bg-gradient-hero bg-clip-text text-transparent drop-shadow-sm">
                Expense Approvals with AI
              </span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Smart, transparent, and flexible reimbursement workflows for global teams. 
              Streamline expense management from submission to payment.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/company-registration">
                <Button size="lg" variant="hero" className="w-full sm:w-auto shadow-glow">
                  Register Your Company
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/auth">
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-muted/50">
        <div className="container">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold">
              Everything you need to manage expenses
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Powerful features designed to simplify expense management for teams of all sizes
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="p-6 hover:shadow-elegant transition-all duration-300 border-none bg-gradient-soft">
              <div className="w-20 h-20 mx-auto mb-4">
                <img src={ocrImage} alt="OCR scanning" className="w-full h-full object-contain drop-shadow-lg" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Smart OCR-based Entry</h3>
              <p className="text-muted-foreground">
                Simply snap a photo of your receipt. Our AI automatically extracts amount, 
                date, category, and vendor information.
              </p>
            </Card>

            <Card className="p-6 hover:shadow-elegant transition-all duration-300 border-none bg-gradient-soft">
              <div className="w-20 h-20 mx-auto mb-4">
                <img src={approvalImage} alt="Approval workflow" className="w-full h-full object-contain drop-shadow-lg" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Multi-level Approvals</h3>
              <p className="text-muted-foreground">
                Set up conditional approval workflows based on amount, category, or department. 
                Flexible rules that scale with your organization.
              </p>
            </Card>

            <Card className="p-6 hover:shadow-elegant transition-all duration-300 border-none bg-gradient-soft">
              <div className="w-20 h-20 mx-auto mb-4">
                <img src={dashboardImage} alt="Analytics dashboard" className="w-full h-full object-contain drop-shadow-lg" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Real-time Dashboards</h3>
              <p className="text-muted-foreground">
                Monitor spending patterns, approval times, and budget utilization with 
                beautiful, interactive charts and reports.
              </p>
            </Card>

            <Card className="p-6 hover:shadow-lg transition-shadow duration-200 border-2">
              <div className="h-12 w-12 rounded-lg bg-success/10 flex items-center justify-center mb-4">
                <Globe className="h-6 w-6 text-success" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Multi-currency Support</h3>
              <p className="text-muted-foreground">
                Handle expenses in any currency with automatic conversion. Perfect for 
                distributed teams working across borders.
              </p>
            </Card>

            <Card className="p-6 hover:shadow-lg transition-shadow duration-200 border-2">
              <div className="h-12 w-12 rounded-lg bg-warning/10 flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-warning" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Audit Trail</h3>
              <p className="text-muted-foreground">
                Complete visibility into every action. Track who approved what, when, and why 
                for full compliance and transparency.
              </p>
            </Card>

            <Card className="p-6 hover:shadow-lg transition-shadow duration-200 border-2">
              <div className="h-12 w-12 rounded-lg bg-destructive/10 flex items-center justify-center mb-4">
                <FileText className="h-6 w-6 text-destructive" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Export & Integrate</h3>
              <p className="text-muted-foreground">
                Export reports in multiple formats. Integrate with your existing accounting 
                and payroll systems seamlessly.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* Currency Support Section */}
      <section className="py-16">
        <div className="container">
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-3xl font-bold">Supported Currencies</h2>
            <p className="text-muted-foreground">Work with teams across the globe</p>
          </div>
          <div className="flex flex-wrap justify-center gap-8 items-center opacity-60">
            <div className="flex items-center gap-2">
              <span className="text-3xl">🇺🇸</span>
              <span className="font-medium">USD</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-3xl">🇪🇺</span>
              <span className="font-medium">EUR</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-3xl">🇬🇧</span>
              <span className="font-medium">GBP</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-3xl">🇯🇵</span>
              <span className="font-medium">JPY</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-3xl">🇨🇦</span>
              <span className="font-medium">CAD</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-3xl">🇦🇺</span>
              <span className="font-medium">AUD</span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-hero text-primary-foreground relative overflow-hidden">
        <div className="absolute inset-0 opacity-5 bg-cover bg-center" style={{ backgroundImage: `url(${heroImage})` }} />
        <div className="absolute inset-0 bg-gradient-overlay" />
        <div className="container relative text-center space-y-8">
          <h2 className="text-3xl md:text-4xl font-bold drop-shadow-lg">
            Ready to streamline your expense management?
          </h2>
          <p className="text-lg text-primary-foreground/95 max-w-2xl mx-auto drop-shadow">
            Join thousands of companies that trust ExpenseFlow for their reimbursement workflows
          </p>
          <Link to="/company-registration">
            <Button size="lg" variant="secondary" className="shadow-glow">
              Register Your Company
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12 bg-muted/30">
        <div className="container">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-gradient-hero" />
                <span className="text-lg font-bold">ExpenseFlow</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Modern expense management for modern teams
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Security</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">About</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Privacy</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-border text-center text-sm text-muted-foreground">
            © 2024 ExpenseFlow. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
