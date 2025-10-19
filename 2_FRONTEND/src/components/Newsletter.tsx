
import { useState, useRef, useEffect } from "react";
import { Mail } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Newsletter() {
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isIntersecting, setIsIntersecting] = useState(false);
  const sectionRef = useRef<HTMLDivElement>(null);
  
  // Intersection observer to trigger animation when section is in view
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
      },
      { threshold: 0.1 }
    );
    
    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }
    
    return () => observer.disconnect();
  }, []);
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) return;
    
    setIsSubmitting(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      setIsSuccess(true);
      setEmail("");
      
      // Reset success message after 3 seconds
      setTimeout(() => {
        setIsSuccess(false);
      }, 3000);
    }, 1000);
  };

  return (
    <section 
      ref={sectionRef}
      className="bg-gray-50 py-24"
    >
      <div className="section-container">
        <div 
          className={cn(
            "max-w-xl mx-auto text-center transition-all duration-500",
            isIntersecting ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
          )}
        >
          <Mail className="h-12 w-12 mx-auto mb-6 text-primary opacity-80" />
          <h2 className="text-3xl font-medium tracking-tight text-gray-900">
            Stay in Touch
          </h2>
          <p className="mt-4 text-lg text-gray-500">
            Subscribe to our newsletter for exclusive offers, early access to new collections, and styled inspiration.
          </p>
          
          <form 
            onSubmit={handleSubmit}
            className="mt-8 flex flex-col sm:flex-row gap-3"
          >
            <div className="relative flex-grow">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="input-field w-full"
                disabled={isSubmitting}
                required
              />
            </div>
            <button
              type="submit"
              className={cn(
                "btn-primary whitespace-nowrap transition-all duration-200",
                isSubmitting && "opacity-80 cursor-not-allowed"
              )}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Subscribing..." : "Subscribe"}
            </button>
          </form>
          
          {isSuccess && (
            <div className="mt-4 text-green-600 text-sm font-medium animate-fade-in">
              Thank you for subscribing!
            </div>
          )}
          
          <p className="mt-4 text-xs text-gray-500">
            By subscribing, you agree to our Privacy Policy and consent to receive updates from our company.
          </p>
        </div>
      </div>
    </section>
  );
}
