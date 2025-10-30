
import { useEffect, useState, useRef } from "react";
import { ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

// Array of hero images
const heroImages = [
  "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=2070&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=2124&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=2070&auto=format&fit=crop"
];

export default function HeroSection() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [imagesLoaded, setImagesLoaded] = useState<boolean[]>([]);
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
  
  // Preload images
  useEffect(() => {
    const loadStatus = Array(heroImages.length).fill(false);
    
    heroImages.forEach((src, index) => {
      const img = new Image();
      img.src = src;
      img.onload = () => {
        loadStatus[index] = true;
        setImagesLoaded([...loadStatus]);
      };
    });
  }, []);
  
  // Rotate through hero images
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((prevIndex) => (prevIndex + 1) % heroImages.length);
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <section 
      ref={sectionRef} 
      className="relative overflow-hidden bg-gray-50 pt-16"
    >
      {/* Hero image background */}
      <div className="absolute inset-0 overflow-hidden">
        {heroImages.map((image, index) => (
          <div
            key={index}
            className={cn(
              "absolute inset-0 transition-opacity duration-1000 ease-in-out",
              activeIndex === index ? "opacity-100" : "opacity-0"
            )}
          >
            <div className={cn(
              "absolute inset-0 bg-black/20",
              imagesLoaded[index] ? "opacity-100" : "opacity-0",
              "transition-opacity duration-500"
            )} />
            <img
              src={image}
              alt={`Hero image ${index + 1}`}
              className={cn(
                "h-full w-full object-cover object-center",
                imagesLoaded[index] ? "opacity-100" : "opacity-0",
                "transition-opacity duration-500",
                activeIndex === index ? "scale-105" : "scale-100",
                "transform transition-transform duration-6000 ease-out"
              )}
            />
          </div>
        ))}
      </div>
      
      {/* Content */}
      <div className="relative mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8 lg:py-40">
        <div 
          className={cn(
            "max-w-2xl stagger-animation",
            isIntersecting && "appear"
          )}
        >
          <div className="inline-block rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
            Summer Collection 2023
          </div>
          <h1 className="mt-6 text-4xl font-medium tracking-tight text-white sm:text-5xl lg:text-6xl">
            Elevate Your Style <br /> With Timeless Pieces
          </h1>
          <p className="mt-6 text-lg text-white/90 max-w-lg">
            Discover our latest collection of thoughtfully designed, high-quality garments that blend classic elegance with contemporary style.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row gap-4">
            <a
              href="/shop"
              className="btn-primary flex items-center justify-center bg-white text-primary"
            >
              Shop Collection
              <ArrowRight className="ml-2 h-4 w-4" />
            </a>
            <a
              href="/lookbook"
              className="btn-secondary bg-transparent border border-white text-white hover:bg-white/10"
            >
              View Lookbook
            </a>
          </div>
        </div>
      </div>
      
      {/* Image indicators */}
      <div className="absolute bottom-8 left-0 right-0 flex justify-center gap-2">
        {heroImages.map((_, index) => (
          <button
            key={index}
            onClick={() => setActiveIndex(index)}
            className={cn(
              "w-2 h-2 rounded-full transition-all duration-300",
              activeIndex === index
                ? "bg-white w-8"
                : "bg-white/50 hover:bg-white/80"
            )}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>
    </section>
  );
}
