
import { useEffect, useRef, useState } from "react";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import FeaturedSection from "@/components/FeaturedSection";
import Newsletter from "@/components/Newsletter";
import Footer from "@/components/Footer";
import ProductCard from "@/components/ProductCard";
import { cn } from "@/lib/utils";
import { ArrowRight, Star } from "lucide-react";

// Sample product data
const newArrivals = [
  {
    id: "1",
    name: "Tailored Linen Blazer",
    price: 19999,  // Updated price for INR
    image: "https://images.unsplash.com/photo-1598522337630-9243f3e7bf9f?q=80&w=1974&auto=format&fit=crop",
    isNew: true,
    category: "Outerwear",
  },
  {
    id: "2",
    name: "Slim Fit Cotton Shirt",
    price: 7999,  // Updated price for INR
    image: "https://images.unsplash.com/photo-1617127365659-c47fa864d8bc?q=80&w=1974&auto=format&fit=crop",
    isNew: true,
    category: "Shirts",
  },
  {
    id: "3",
    name: "Wool Blend Trousers",
    price: 12999,  // Updated price for INR
    image: "https://images.unsplash.com/photo-1509946458702-4378df1e2560?q=80&w=1974&auto=format&fit=crop",
    isNew: true,
    category: "Bottoms",
  },
  {
    id: "4",
    name: "Lightweight Overcoat",
    price: 24999,  // Updated price for INR
    image: "https://images.unsplash.com/photo-1541346160430-93fcee38d521?q=80&w=1974&auto=format&fit=crop",
    isNew: true,
    category: "Outerwear",
  },
];

const bestSellers = [
  {
    id: "5",
    name: "Classic White Tee",
    price: 4999,  // Updated price for INR
    image: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=1780&auto=format&fit=crop",
    category: "Tops",
  },
  {
    id: "6",
    name: "Selvedge Denim Jeans",
    price: 14999,  // Updated price for INR
    image: "https://images.unsplash.com/photo-1604176424472-17cd740f74e9?q=80&w=1780&auto=format&fit=crop",
    category: "Bottoms",
  },
  {
    id: "7",
    name: "Chelsea Leather Boots",
    price: 17999,  // Updated price for INR
    image: "https://images.unsplash.com/photo-1638247025967-b4e38f787b76?q=80&w=1935&auto=format&fit=crop",
    category: "Footwear",
  },
  {
    id: "8",
    name: "Cashmere Sweater",
    price: 18999,  // Updated price for INR
    image: "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=1964&auto=format&fit=crop",
    category: "Knitwear",
  },
];

const promotions = [
  {
    id: "summer-sale",
    title: "Summer Sale",
    description: "Enjoy up to 40% off select summer styles",
    code: "SUMMER40",
    background: "bg-amber-50",
    textColor: "text-amber-900",
    codeBackground: "bg-amber-100",
  },
  {
    id: "free-shipping",
    title: "Free Shipping",
    description: "On all orders over $150",
    code: "FREESHIP",
    background: "bg-blue-50",
    textColor: "text-blue-900",
    codeBackground: "bg-blue-100",
  },
];

const testimonials = [
  {
    id: "1",
    name: "Sarah Johnson",
    role: "Fashion Designer",
    quote: "The quality of VALORA's clothing is exceptional. The attention to detail and craftsmanship is evident in every piece.",
    rating: 5,
    image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=1974&auto=format&fit=crop",
  },
  {
    id: "2",
    name: "Michael Chen",
    role: "Creative Director",
    quote: "I've been a loyal customer for years. Their timeless designs perfectly balance contemporary trends with classic elements.",
    rating: 5,
    image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1974&auto=format&fit=crop",
  },
  {
    id: "3",
    name: "Emma Thompson",
    role: "Stylist",
    quote: "VALORA pieces are my go-to recommendation for clients looking for versatile, high-quality garments that last.",
    rating: 4,
    image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1961&auto=format&fit=crop",
  },
];

export default function Index() {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  
  // Refs for intersection animations
  const newArrivalsRef = useRef<HTMLDivElement>(null);
  const bestSellersRef = useRef<HTMLDivElement>(null);
  const promotionsRef = useRef<HTMLDivElement>(null);
  const testimonialsRef = useRef<HTMLDivElement>(null);
  
  // Intersection states
  const [newArrivalsVisible, setNewArrivalsVisible] = useState(false);
  const [bestSellersVisible, setBestSellersVisible] = useState(false);
  const [promotionsVisible, setPromotionsVisible] = useState(false);
  const [testimonialsVisible, setTestimonialsVisible] = useState(false);
  
  // Set up intersection observers
  useEffect(() => {
    const options = { threshold: 0.1 };
    
    const newArrivalsObserver = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) setNewArrivalsVisible(true);
    }, options);
    
    const bestSellersObserver = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) setBestSellersVisible(true);
    }, options);
    
    const promotionsObserver = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) setPromotionsVisible(true);
    }, options);
    
    const testimonialsObserver = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) setTestimonialsVisible(true);
    }, options);
    
    if (newArrivalsRef.current) newArrivalsObserver.observe(newArrivalsRef.current);
    if (bestSellersRef.current) bestSellersObserver.observe(bestSellersRef.current);
    if (promotionsRef.current) promotionsObserver.observe(promotionsRef.current);
    if (testimonialsRef.current) testimonialsObserver.observe(testimonialsRef.current);
    
    return () => {
      newArrivalsObserver.disconnect();
      bestSellersObserver.disconnect();
      promotionsObserver.disconnect();
      testimonialsObserver.disconnect();
    };
  }, []);
  
  // Rotate testimonials
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      
      <main>
        <HeroSection />
        
        <FeaturedSection />
        
        {/* New Arrivals Section */}
        <section 
          ref={newArrivalsRef}
          className="section-container"
        >
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12">
            <div>
              <h2 className="text-3xl font-medium tracking-tight text-gray-900">
                New Arrivals
              </h2>
              <p className="mt-4 text-lg text-gray-500 max-w-2xl">
                Explore our latest additions to elevate your wardrobe this season.
              </p>
            </div>
            <a
              href="/new-arrivals"
              className="mt-6 md:mt-0 text-sm font-medium text-primary hover:text-primary/80 flex items-center group"
            >
              View All
              <ArrowRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </a>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
            {newArrivals.map((product, index) => (
              <div
                key={product.id}
                className={cn(
                  "transition-all duration-500",
                  newArrivalsVisible ? 
                    `opacity-100 translate-y-0 delay-[${index * 100}ms]` : 
                    "opacity-0 translate-y-8"
                )}
                style={{
                  transitionDelay: `${index * 100}ms`,
                }}
              >
                <ProductCard {...product} />
              </div>
            ))}
          </div>
        </section>
        
        {/* Promotion Banners */}
        <section 
          ref={promotionsRef}
          className="section-container"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {promotions.map((promo, index) => (
              <div
                key={promo.id}
                className={cn(
                  "rounded-xl p-8 transition-all duration-500",
                  promo.background,
                  promotionsVisible ? 
                    `opacity-100 translate-y-0 delay-[${index * 150}ms]` : 
                    "opacity-0 translate-y-12"
                )}
                style={{
                  transitionDelay: `${index * 150}ms`,
                }}
              >
                <h3 className={cn("text-2xl font-medium", promo.textColor)}>
                  {promo.title}
                </h3>
                <p className={cn("mt-2 text-sm opacity-90", promo.textColor)}>
                  {promo.description}
                </p>
                <div className="mt-4 flex items-center">
                  <span className={cn(
                    "inline-block px-3 py-1 text-xs font-mono rounded",
                    promo.codeBackground,
                    promo.textColor
                  )}>
                    {promo.code}
                  </span>
                  <button
                    className={cn(
                      "ml-4 text-xs font-medium underline",
                      promo.textColor
                    )}
                  >
                    Copy code
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
        
        {/* Best Sellers Section */}
        <section 
          ref={bestSellersRef}
          className="section-container"
        >
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12">
            <div>
              <h2 className="text-3xl font-medium tracking-tight text-gray-900">
                Best Sellers
              </h2>
              <p className="mt-4 text-lg text-gray-500 max-w-2xl">
                Our most popular pieces loved by customers around the world.
              </p>
            </div>
            <a
              href="/best-sellers"
              className="mt-6 md:mt-0 text-sm font-medium text-primary hover:text-primary/80 flex items-center group"
            >
              View All
              <ArrowRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </a>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
            {bestSellers.map((product, index) => (
              <div
                key={product.id}
                className={cn(
                  "transition-all duration-500",
                  bestSellersVisible ? 
                    `opacity-100 translate-y-0 delay-[${index * 100}ms]` : 
                    "opacity-0 translate-y-8"
                )}
                style={{
                  transitionDelay: `${index * 100}ms`,
                }}
>
                <ProductCard {...product} />
              </div>
            ))}
          </div>
        </section>
        
        {/* Testimonials */}
        <section 
          ref={testimonialsRef}
          className="section-container"
        >
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-medium tracking-tight text-gray-900">
              Customer Reviews
            </h2>
            <p className="mt-4 text-lg text-gray-500 max-w-2xl mx-auto">
              Hear what our customers have to say about their experience with VALORA.
            </p>
          </div>
          
          <div className="relative max-w-3xl mx-auto">
            {testimonials.map((testimonial, index) => (
              <div
                key={testimonial.id}
                className={cn(
                  "absolute inset-0 transition-all duration-1000 ease-in-out flex flex-col items-center text-center",
                  index === currentTestimonial 
                    ? "opacity-100 translate-y-0" 
                    : "opacity-0 translate-y-8 pointer-events-none"
                )}
                style={{
                  position: index === currentTestimonial ? "relative" : "absolute"
                }}
              >
                <div className="w-20 h-20 rounded-full overflow-hidden mb-6 ring-2 ring-primary/10">
                  <img
                    src={testimonial.image}
                    alt={testimonial.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={cn(
                        "h-5 w-5", 
                        i < testimonial.rating ? "text-amber-400 fill-amber-400" : "text-gray-300"
                      )}
                    />
                  ))}
                </div>
                
                <blockquote className="text-xl italic text-gray-700 mb-6">
                  "{testimonial.quote}"
                </blockquote>
                
                <div>
                  <p className="font-medium text-gray-900">{testimonial.name}</p>
                  <p className="text-sm text-gray-500">{testimonial.role}</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="flex justify-center mt-8 gap-2">
            {testimonials.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentTestimonial(index)}
                className={cn(
                  "w-2 h-2 rounded-full transition-all duration-300",
                  index === currentTestimonial
                    ? "bg-primary w-8"
                    : "bg-gray-300 hover:bg-gray-400"
                )}
                aria-label={`Go to testimonial ${index + 1}`}
              />
            ))}
          </div>
        </section>
        
        <Newsletter />
      </main>
      
      <Footer />
    </div>
  );
}
