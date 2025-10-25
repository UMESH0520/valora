
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Menu, X, ShoppingBag, User, Search } from "lucide-react";
import { Link } from "react-router-dom";

const navigation = [
  { name: "Home", href: "/" },
  { name: "Shop", href: "/shop" },
  { name: "Hoodies", href: "/hoodies" },
  { name: "Jeans", href: "/jeans" },
  { name: "Blazers", href: "/blazers" },
  { name: "Women Tops", href: "/women-tops" },
  { name: "New Arrivals", href: "/new-arrivals" },
];

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Detect scroll to change navbar appearance
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed top-0 inset-x-0 z-50 transition-all duration-300 ease-in-out",
        isScrolled
          ? "bg-white/80 backdrop-blur-md border-b shadow-sm py-3"
          : "bg-transparent py-5"
      )}
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 lg:px-8">
        {/* Logo */}
        <div className="flex lg:flex-1">
          <Link 
            to="/"
            className="font-display text-xl font-semibold tracking-tighter"
          >
            VALORA
          </Link>
        </div>
        
        {/* Mobile menu button */}
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <span className="sr-only">Open main menu</span>
            {mobileMenuOpen ? (
              <X className="h-6 w-6" aria-hidden="true" />
            ) : (
              <Menu className="h-6 w-6" aria-hidden="true" />
            )}
          </button>
        </div>
        
        {/* Desktop navigation */}
        <div className="hidden lg:flex lg:gap-x-8">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className="navbar-link"
            >
              {item.name}
            </Link>
          ))}
        </div>
        
        {/* Right side icons: search, account, cart */}
        <div className="hidden lg:flex lg:flex-1 lg:justify-end lg:gap-x-6">
          <button className="text-sm text-gray-700 hover:text-gray-900 transition-colors">
            <Search className="h-5 w-5" />
          </button>
          <Link to="/account" className="text-sm text-gray-700 hover:text-gray-900 transition-colors">
            <User className="h-5 w-5" />
          </Link>
          <Link to="/cart" className="text-sm text-gray-700 hover:text-gray-900 transition-colors flex items-center">
            <ShoppingBag className="h-5 w-5" />
            <span className="ml-1 text-xs bg-primary text-white rounded-full w-4 h-4 flex items-center justify-center">
              0
            </span>
          </Link>
        </div>
      </nav>
      
      {/* Mobile menu, show/hide based on menu state */}
      <div
        className={cn(
          "fixed inset-0 z-50 bg-white/95 backdrop-blur-sm transition-all duration-300 ease-in-out lg:hidden",
          mobileMenuOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
      >
        <div className="flex flex-col h-full pt-16 pb-6 px-6">
          <div className="flex items-center justify-end">
            <button
              type="button"
              className="-m-2.5 rounded-md p-2.5 text-gray-700"
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="sr-only">Close menu</span>
              <X className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div className="mt-8 space-y-6 flex flex-col items-center">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="text-base font-medium text-gray-900 hover-underline"
                onClick={() => setMobileMenuOpen(false)}
              >
                {item.name}
              </Link>
            ))}
          </div>
          <div className="mt-auto flex justify-center space-x-8">
            <Link to="/search" className="text-gray-700 hover:text-gray-900">
              <Search className="h-6 w-6" />
            </Link>
            <Link to="/account" className="text-gray-700 hover:text-gray-900">
              <User className="h-6 w-6" />
            </Link>
            <Link to="/cart" className="text-gray-700 hover:text-gray-900 relative">
              <ShoppingBag className="h-6 w-6" />
              <span className="absolute -top-1 -right-1 text-xs bg-primary text-white rounded-full w-4 h-4 flex items-center justify-center">
                0
              </span>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
