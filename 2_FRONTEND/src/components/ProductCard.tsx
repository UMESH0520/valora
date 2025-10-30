
import { useState } from "react";
import { ShoppingBag, Heart, ChevronLeft, ChevronRight, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLivePrice } from "@/hooks/useLivePrice";
import { mapFrontendToBackendId } from "@/lib/productIdMap";

interface ProductCardProps {
  id: string;
  name: string;
  price: number;
  image: string;
  images?: string[];
  description?: string;
  sizes?: string[];
  isNew?: boolean;
  isSale?: boolean;
  discount?: number;
  category?: string;
  className?: string;
}

export default function ProductCard({
  id,
  name,
  price,
  image,
  images = [],
  description = "",
  sizes = [],
  isNew = false,
  isSale = false,
  discount = 0,
  category = "",
  className,
}: ProductCardProps) {
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isDetailView, setIsDetailView] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [selectedSize, setSelectedSize] = useState("");

  const allImages = [image, ...(images || [])];

  const backendId = mapFrontendToBackendId(id) || id
  const { 
    displayRupees, 
    isUpdating, 
    triggerPriceUpdate,
  } = useLivePrice(backendId)

  const effectivePrice = typeof displayRupees === 'number' ? displayRupees : price

  const formattedPrice = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(effectivePrice);

  const discountedPrice = discount
    ? new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0,
      }).format(effectivePrice - (effectivePrice * discount) / 100)
    : null;

  const handlePrevImage = (e: React.MouseEvent) => {
    e.stopPropagation();
    setCurrentImageIndex((prev) => (prev === 0 ? allImages.length - 1 : prev - 1));
  };

  const handleNextImage = (e: React.MouseEvent) => {
    e.stopPropagation();
    setCurrentImageIndex((prev) => (prev === allImages.length - 1 ? 0 : prev + 1));
  };

  const handleSizeSelect = (size: string) => {
    setSelectedSize(size);
  };

  // Basic card view
  if (!isDetailView) {
    return (
      <div 
        className={cn(
          "group relative overflow-hidden product-card-hover rounded-lg cursor-pointer",
          className
        )}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={() => setIsDetailView(true)}
      >
        {/* Product image container */}
        <div className="aspect-[3/4] overflow-hidden rounded-lg bg-gray-50">
          <div className={cn(
            "w-full h-full relative",
            !isImageLoaded && "image-loading"
          )}>
            <img
              src={image}
              alt={name}
              className={cn(
                "h-full w-full object-cover object-center transition-all duration-500",
                isHovered ? "scale-105" : "scale-100",
                isImageLoaded ? "opacity-100" : "opacity-0"
              )}
              onLoad={() => setIsImageLoaded(true)}
            />
            
            {/* Badges */}
            <div className="absolute top-2 left-2 flex flex-col gap-2">
              {isNew && (
                <span className="inline-flex items-center rounded-full bg-primary px-2 py-1 text-xs font-medium text-white animate-fade-in-fast">
                  New
                </span>
              )}
              {isSale && (
                <span className="inline-flex items-center rounded-full bg-red-600 px-2 py-1 text-xs font-medium text-white animate-fade-in-fast">
                  Sale
                </span>
              )}
            </div>
            
            {/* Price update button - visible on hover */}
            <div className={cn(
              "absolute top-2 right-2 opacity-0 transition-opacity duration-300",
              isHovered && "opacity-100"
            )}>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  triggerPriceUpdate();
                }}
                disabled={isUpdating}
                className={cn(
                  "rounded-full bg-white/90 p-2 shadow-md transition-all hover:bg-white active:scale-95",
                  isUpdating && "animate-spin"
                )}
                title="Update price from blockchain"
              >
                <RefreshCw className="h-4 w-4 text-gray-700" />
              </button>
            </div>
            
            {/* Quick actions - visible on hover */}
            <div className={cn(
              "absolute inset-0 flex items-center justify-center gap-2 bg-black/5 backdrop-blur-sm opacity-0 transition-opacity duration-300",
              isHovered && "opacity-100"
            )}>
              <button className="rounded-full bg-white p-3 shadow-md transition-transform hover:scale-105 active:scale-95">
                <ShoppingBag className="h-5 w-5" />
              </button>
              <button className="rounded-full bg-white p-3 shadow-md transition-transform hover:scale-105 active:scale-95">
                <Heart className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
        
        {/* Product info */}
        <div className="mt-4 flex flex-col">
          {category && (
            <span className="text-xs text-gray-500 uppercase tracking-wider mb-1">
              {category}
            </span>
          )}
          <h3 className="text-sm font-medium text-gray-900 transition-colors group-hover:text-primary">
            {name}
          </h3>
          <div className="mt-1 flex items-center justify-between">
            <div className="flex items-center">
              {discountedPrice ? (
                <>
                  <span className="text-sm font-medium text-gray-900">{discountedPrice}</span>
                  <span className="ml-2 text-xs text-gray-500 line-through">{formattedPrice}</span>
                </>
              ) : (
                <span className="text-sm font-medium text-gray-900">{formattedPrice}</span>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Detailed view
  return (
    <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4 overflow-y-auto" onClick={() => setIsDetailView(false)}>
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Image gallery */}
          <div className="relative overflow-hidden rounded-lg bg-gray-50">
            <div className="aspect-[3/4] md:sticky md:top-6">
              <img
                src={allImages[currentImageIndex]}
                alt={`${name} - view ${currentImageIndex + 1}`}
                className="h-full w-full object-cover object-center"
              />
              
              {/* Image navigation */}
              <button 
                className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/80 rounded-full p-2 shadow-md"
                onClick={handlePrevImage}
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <button 
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/80 rounded-full p-2 shadow-md"
                onClick={handleNextImage}
              >
                <ChevronRight className="h-5 w-5" />
              </button>
              
              {/* Image pagination */}
              <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-1.5">
                {allImages.map((_, index) => (
                  <button
                    key={index}
                    className={cn(
                      "w-2 h-2 rounded-full transition-all",
                      currentImageIndex === index ? "bg-primary w-4" : "bg-gray-300"
                    )}
                    onClick={(e) => {
                      e.stopPropagation();
                      setCurrentImageIndex(index);
                    }}
                  />
                ))}
              </div>
            </div>
            
            {/* Thumbnail gallery */}
            <div className="hidden md:flex mt-4 gap-2 overflow-x-auto pb-2">
              {allImages.map((img, index) => (
                <button
                  key={index}
                  className={cn(
                    "flex-shrink-0 w-16 h-16 rounded-md overflow-hidden border-2 transition-all",
                    currentImageIndex === index ? "border-primary" : "border-transparent"
                  )}
                  onClick={(e) => {
                    e.stopPropagation();
                    setCurrentImageIndex(index);
                  }}
                >
                  <img src={img} alt={`${name} thumbnail ${index + 1}`} className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          </div>
          
          {/* Product details */}
          <div className="flex flex-col">
            {category && (
              <span className="text-sm text-gray-500 uppercase tracking-wider">
                {category}
              </span>
            )}
            <h1 className="text-2xl font-semibold text-gray-900 mt-1">{name}</h1>
            
            <div className="mt-2 flex items-center">
              {discountedPrice ? (
                <>
                  <span className="text-xl font-medium text-gray-900">{discountedPrice}</span>
                  <span className="ml-2 text-sm text-gray-500 line-through">{formattedPrice}</span>
                </>
              ) : (
                <span className="text-xl font-medium text-gray-900">{formattedPrice}</span>
              )}
            </div>
            
            {/* Description */}
            {description && (
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-900">Description</h3>
                <div className="mt-2 prose prose-sm text-gray-600" dangerouslySetInnerHTML={{ __html: description }} />
              </div>
            )}
            
            {/* Size selection */}
            {sizes.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-900">Size</h3>
                <div className="mt-2 flex flex-wrap gap-2">
                  {sizes.map((size) => (
                    <button
                      key={size}
                      className={cn(
                        "px-3 py-1 rounded-md text-sm font-medium border transition-all",
                        selectedSize === size
                          ? "border-primary bg-primary text-white"
                          : "border-gray-300 text-gray-700 hover:border-gray-400"
                      )}
                      onClick={() => handleSizeSelect(size)}
                    >
                      {size}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            {/* Add to cart */}
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <button className="btn-primary flex-1 flex items-center justify-center gap-2">
                <ShoppingBag className="h-5 w-5" />
                Add to Bag
              </button>
              <button className="btn-secondary flex items-center justify-center gap-2">
                <Heart className="h-5 w-5" />
                Save
              </button>
            </div>
            
            {/* Additional product info */}
            <div className="mt-8 border-t border-gray-200 pt-6">
              <div className="text-sm text-gray-600">
                <p>• Free shipping for orders over $100</p>
                <p>• 30-day returns</p>
                <p>• 100% Authentic</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
