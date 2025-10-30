
import { useRef, useState, useEffect } from "react";
import { ArrowRight, ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";

interface FeaturedCollectionProps {
  title: string;
  description: string;
  image: string;
  link: string;
}

const featuredCollections: FeaturedCollectionProps[] = [
  {
    title: "Summer Essentials",
    description: "Lightweight fabrics designed for comfort in the heat",
    image: "https://images.unsplash.com/photo-1469334031218-e382a71b716b?q=80&w=2070&auto=format&fit=crop",
    link: "/collections/summer",
  },
  {
    title: "Formal Collection",
    description: "Sophisticated pieces for professional settings",
    image: "https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?q=80&w=2070&auto=format&fit=crop",
    link: "/collections/formal",
  },
  {
    title: "Street Style",
    description: "Urban-inspired designs for everyday wear",
    image: "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?q=80&w=2074&auto=format&fit=crop",
    link: "/collections/street",
  },
];

export default function FeaturedSection() {
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
    const loadStatus = Array(featuredCollections.length).fill(false);
    
    featuredCollections.forEach((collection, index) => {
      const img = new Image();
      img.src = collection.image;
      img.onload = () => {
        loadStatus[index] = true;
        setImagesLoaded([...loadStatus]);
      };
    });
  }, []);

  return (
    <section 
      ref={sectionRef}
      className="section-container overflow-hidden"
    >
      <div className="mb-12 text-center">
        <h2 className="text-3xl font-medium tracking-tight text-gray-900">
          Featured Collections
        </h2>
        <p className="mt-4 text-lg text-gray-500 max-w-2xl mx-auto">
          Explore our curated collections designed for every occasion and style preference.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {featuredCollections.map((collection, index) => (
          <div
            key={index}
            className={cn(
              "group relative overflow-hidden rounded-xl transition-all duration-500",
              isIntersecting ? 
                `opacity-100 translate-y-0 delay-[${index * 100}ms]` : 
                "opacity-0 translate-y-8"
            )}
            style={{
              transitionDelay: `${index * 100}ms`,
            }}
          >
            <div className={cn(
              "aspect-[4/5] bg-gray-100",
              !imagesLoaded[index] && "image-loading"
            )}>
              <img
                src={collection.image}
                alt={collection.title}
                className={cn(
                  "h-full w-full object-cover transition-all duration-700",
                  imagesLoaded[index] ? "opacity-100" : "opacity-0",
                  "group-hover:scale-105"
                )}
              />
            </div>
            
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent flex flex-col justify-end p-6 text-white">
              <h3 className="text-xl font-semibold tracking-tight">{collection.title}</h3>
              <p className="mt-2 text-sm text-white/80">{collection.description}</p>
              <a
                href={collection.link}
                className="mt-4 inline-flex items-center text-sm font-medium text-white transition-colors hover:text-white/80"
              >
                Explore Collection
                <ArrowRight className="ml-1 h-4 w-4" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
