
import { Instagram, Facebook, Twitter } from "lucide-react";
import { Link } from "react-router-dom";

const navigation = {
  shop: [
    { name: "All Products", href: "/shop" },
    { name: "Hoodies", href: "/hoodies" },
    { name: "Jeans", href: "/jeans" },
    { name: "Blazers", href: "/blazers" },
    { name: "Women Tops", href: "/women-tops" },
    { name: "New Arrivals", href: "/new-arrivals" },
  ],
  company: [
    { name: "About Us", href: "/about" },
    { name: "Blog", href: "/blog" },
    { name: "Careers", href: "/careers" },
    { name: "Contact Us", href: "/contact" },
  ],
  support: [
    { name: "Shipping & Returns", href: "/shipping" },
    { name: "FAQ", href: "/faq" },
    { name: "Size Guide", href: "/size-guide" },
    { name: "Privacy Policy", href: "/privacy" },
    { name: "Terms of Service", href: "/terms" },
  ],
  social: [
    {
      name: "Instagram",
      href: "https://instagram.com",
      icon: Instagram,
    },
    {
      name: "Facebook",
      href: "https://facebook.com",
      icon: Facebook,
    },
    {
      name: "Twitter",
      href: "https://twitter.com",
      icon: Twitter,
    },
  ],
};

const paymentMethods = [
  { name: "Visa", image: "https://cdn-icons-png.flaticon.com/128/196/196578.png" },
  { name: "Mastercard", image: "https://cdn-icons-png.flaticon.com/128/196/196561.png" },
  { name: "American Express", image: "https://cdn-icons-png.flaticon.com/128/196/196539.png" },
  { name: "PayPal", image: "https://cdn-icons-png.flaticon.com/128/196/196565.png" },
];

export default function Footer() {
  return (
    <footer className="bg-white" aria-labelledby="footer-heading">
      <h2 id="footer-heading" className="sr-only">
        Footer
      </h2>
      <div className="section-container border-t border-gray-200 pt-12">
        <div className="xl:grid xl:grid-cols-3 xl:gap-8">
          <div className="space-y-8">
            <Link to="/" className="font-display text-2xl font-semibold tracking-tighter">
              VALORA
            </Link>
            <p className="text-gray-500 text-sm max-w-xs">
              Creating timeless pieces that blend elegance with functionality for the modern individual.
            </p>
            <div className="flex space-x-6">
              {navigation.social.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-gray-400 hover:text-gray-500 transition-colors"
                >
                  <span className="sr-only">{item.name}</span>
                  <item.icon className="h-5 w-5" aria-hidden="true" />
                </a>
              ))}
            </div>
          </div>
          <div className="mt-16 grid grid-cols-2 gap-8 xl:col-span-2 xl:mt-0">
            <div className="md:grid md:grid-cols-2 md:gap-8">
              <div>
                <h3 className="text-sm font-semibold text-gray-900">Shop</h3>
                <ul role="list" className="mt-6 space-y-4">
                  {navigation.shop.map((item) => (
                    <li key={item.name}>
                      <Link to={item.href} className="text-sm text-gray-500 hover:text-gray-900 hover-underline">
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="mt-10 md:mt-0">
                <h3 className="text-sm font-semibold text-gray-900">Company</h3>
                <ul role="list" className="mt-6 space-y-4">
                  {navigation.company.map((item) => (
                    <li key={item.name}>
                      <Link to={item.href} className="text-sm text-gray-500 hover:text-gray-900 hover-underline">
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="md:grid md:grid-cols-2 md:gap-8">
              <div>
                <h3 className="text-sm font-semibold text-gray-900">Support</h3>
                <ul role="list" className="mt-6 space-y-4">
                  {navigation.support.map((item) => (
                    <li key={item.name}>
                      <Link to={item.href} className="text-sm text-gray-500 hover:text-gray-900 hover-underline">
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="mt-10 md:mt-0">
                <h3 className="text-sm font-semibold text-gray-900">We Accept</h3>
                <div className="mt-6 flex flex-wrap gap-4">
                  {paymentMethods.map((method) => (
                    <img
                      key={method.name}
                      src={method.image}
                      alt={method.name}
                      className="h-8 w-auto object-contain"
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-12 border-t border-gray-200 pt-8 pb-4">
          <p className="text-xs text-gray-500">
            &copy; {new Date().getFullYear()} VALORA, Inc. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
