
import { useState, useEffect, useMemo } from "react";
import { useCart } from "@/context/CartContext";
import { useToast } from "@/hooks/use-toast";
import { Trash2, Minus, Plus, ArrowRight, ShoppingBag, Heart, Loader2 } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion, AnimatePresence } from "framer-motion";
import { useLivePricesMap } from "@/hooks/useLivePrice";

export default function Cart() {
  const { 
    items, 
    updateQuantity, 
    removeItem, 
    subtotal, 
    appliedCoupon, 
    discount, 
    applyCoupon, 
    removeCoupon,
  } = useCart();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [couponCode, setCouponCode] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isRemoving, setIsRemoving] = useState<string | null>(null);
  const [isQuantityUpdating, setIsQuantityUpdating] = useState<string | null>(null);
  
  // Simulate loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    return () => clearTimeout(timer);
  }, []);
  
  // Live prices map (prices in rupees) -> convert to paise for totals
  const livePrices = useLivePricesMap(items.map(i => i.id))

  const dynamicSubtotal = useMemo(() => {
    return items.reduce((sum, item) => {
      const liveRupees = livePrices[item.id]
      const unitPaise = typeof liveRupees === 'number' ? Math.round(liveRupees * 100) : item.price
      return sum + unitPaise * item.quantity
    }, 0)
  }, [items, livePrices])

  // Calculate final amounts using dynamic subtotal
  const discountAmount = dynamicSubtotal * (discount / 100);
  const shippingFee = dynamicSubtotal > 200000 ? 0 : 9900; // Free shipping over ₹2000
  const taxRate = 0.18; // 18% tax
  const taxAmount = (dynamicSubtotal - discountAmount) * taxRate;
  const totalAmount = dynamicSubtotal - discountAmount + shippingFee + taxAmount;
  
  // Format currency in INR
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(price / 100);
  };

  // Handle quantity update with animation
  const handleQuantityUpdate = async (id: string, newQuantity: number, size?: string) => {
    const itemKey = `${id}-${size || 'default'}`;
    setIsQuantityUpdating(itemKey);
    
    // Add a small delay to make the animation noticeable
    setTimeout(() => {
      updateQuantity(id, newQuantity, size);
      setIsQuantityUpdating(null);
    }, 300);
  };
  
  // Handle item removal with animation
  const handleRemoveItem = async (id: string, size?: string) => {
    const itemKey = `${id}-${size || 'default'}`;
    setIsRemoving(itemKey);
    
    // Add a small delay to make the animation noticeable
    setTimeout(() => {
      removeItem(id, size);
      setIsRemoving(null);
    }, 300);
  };
  
  // Handle coupon application
  const handleApplyCoupon = () => {
    if (couponCode.trim() === "") {
      toast({
        title: "Empty coupon",
        description: "Please enter a coupon code",
        variant: "destructive",
      });
      return;
    }
    
    if (applyCoupon(couponCode)) {
      setCouponCode("");
    }
  };
  
  if (isLoading) {
    return (
      <div className="section-container min-h-[60vh] flex flex-col items-center justify-center">
        <Loader2 className="h-12 w-12 text-primary animate-spin mb-4" />
        <h2 className="text-xl font-medium text-gray-700">Loading your cart...</h2>
      </div>
    );
  }
  
  if (items.length === 0) {
    return (
      <div className="section-container min-h-[60vh] flex flex-col items-center justify-center py-16 px-4">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <ShoppingBag className="h-20 w-20 text-gray-300 mb-6 mx-auto" />
          <h2 className="text-3xl font-medium text-gray-700 mb-4">Your cart is empty</h2>
          <p className="text-gray-500 mb-8 max-w-md mx-auto">
            Looks like you haven't added anything to your cart yet. Browse our collection and find something you'll love.
          </p>
          <Link to="/">
            <Button size="lg" className="px-8">
              Continue Shopping
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="section-container py-16">
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-3xl md:text-4xl font-semibold mb-8">Your Shopping Cart</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items - Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Cart Headers - only visible on larger screens */}
            <div className="hidden md:grid grid-cols-8 py-3 border-b text-sm font-medium text-gray-600">
              <div className="col-span-3">Product</div>
              <div className="col-span-1 text-center">Size</div>
              <div className="col-span-2 text-center">Quantity</div>
              <div className="col-span-1 text-right">Price</div>
              <div className="col-span-1 text-right">Total</div>
            </div>
            
            {/* Cart Items */}
            <AnimatePresence>
              {items.map((item) => {
                const itemKey = `${item.id}-${item.size || 'default'}`;
                const isCurrentlyRemoving = isRemoving === itemKey;
                const isCurrentlyUpdating = isQuantityUpdating === itemKey;
                
                return (
                  <motion.div 
                    key={itemKey}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: isCurrentlyRemoving ? 0.5 : 1, y: 0 }}
                    exit={{ opacity: 0, height: 0, marginBottom: 0, paddingBottom: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`grid grid-cols-1 md:grid-cols-8 gap-4 border-b py-6 items-center ${isCurrentlyRemoving ? 'opacity-50' : ''}`}
                  >
                    {/* Product Info */}
                    <div className="col-span-1 md:col-span-3 flex items-center space-x-4">
                      <Link to={`/product/${item.id}`} className="h-24 w-20 bg-gray-100 rounded-md overflow-hidden flex-shrink-0 hover:opacity-90 transition-opacity">
                        <img 
                          src={item.image} 
                          alt={item.name} 
                          className="h-full w-full object-cover"
                        />
                      </Link>
                      <div>
                        <Link to={`/product/${item.id}`} className="font-medium text-gray-800 hover:text-primary transition-colors">
                          {item.name}
                        </Link>
                        <div className="md:hidden mt-1 flex items-center justify-between">
                          <div className="text-sm text-gray-500">
                            {item.size && <span className="mr-3">Size: {item.size}</span>}
                            <span>Price: {formatPrice(item.price)}</span>
                          </div>
                        </div>
                        <div className="hidden md:flex mt-2 space-x-2">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="h-7 px-2 text-xs text-gray-600 hover:text-primary"
                            onClick={() => handleRemoveItem(item.id, item.size)}
                            disabled={isCurrentlyRemoving}
                          >
                            Remove
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="h-7 px-2 text-xs text-gray-600 hover:text-primary"
                          >
                            <Heart className="h-3 w-3 mr-1" />
                            Save
                          </Button>
                        </div>
                      </div>
                    </div>
                    
                    {/* Size (hidden on mobile) */}
                    <div className="hidden md:block md:col-span-1 text-center text-gray-700">
                      {item.size || "-"}
                    </div>
                    
                    {/* Quantity Controls */}
                    <div className="col-span-1 md:col-span-2 flex items-center justify-between md:justify-center">
                      <motion.button 
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleQuantityUpdate(item.id, item.quantity - 1, item.size)}
                        className="h-9 w-9 flex items-center justify-center rounded-full border hover:bg-gray-100 transition-colors"
                        disabled={isCurrentlyUpdating}
                      >
                        <Minus className="h-3 w-3" />
                      </motion.button>
                      <motion.span 
                        key={item.quantity}
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mx-2 min-w-[2.5rem] text-center font-medium"
                      >
                        {item.quantity}
                      </motion.span>
                      <motion.button 
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleQuantityUpdate(item.id, item.quantity + 1, item.size)}
                        className="h-9 w-9 flex items-center justify-center rounded-full border hover:bg-gray-100 transition-colors"
                        disabled={isCurrentlyUpdating}
                      >
                        <Plus className="h-3 w-3" />
                      </motion.button>
                    </div>
                    
                    {/* Price (hidden on mobile) */}
                      <div className="hidden md:block md:col-span-1 text-right text-gray-700">
                      {(() => {
                        const liveRupees = livePrices[item.id]
                        const unitPaise = typeof liveRupees === 'number' ? Math.round(liveRupees * 100) : item.price
                        return formatPrice(unitPaise)
                      })()}
                    </div>
                    
                    {/* Total */}
                    <div className="col-span-1 flex items-center justify-between md:justify-end md:space-x-4">
                      <span className="md:hidden">Total:</span>
                      <span className="font-medium">{(() => { const liveRupees = livePrices[item.id]; const unitPaise = typeof liveRupees === 'number' ? Math.round(liveRupees * 100) : item.price; return formatPrice(unitPaise * item.quantity) })()}</span>
                      <button 
                        onClick={() => handleRemoveItem(item.id, item.size)}
                        className="text-gray-400 hover:text-red-500 transition-colors md:hidden"
                        aria-label="Remove item"
                        disabled={isCurrentlyRemoving}
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
            
            {/* Continue Shopping Link */}
            <div className="flex justify-start pt-4">
              <Link to="/" className="text-sm font-medium text-primary hover:text-primary/80 flex items-center">
                <ArrowRight className="mr-1 h-4 w-4 rotate-180" />
                Continue Shopping
              </Link>
            </div>
          </div>
          
          {/* Cart Summary - Right Column */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.2 }}
              className="bg-gray-50 rounded-xl p-6 space-y-6 sticky top-20"
            >
              <h2 className="text-xl font-medium text-gray-900">Order Summary</h2>
              
              {/* Coupon Code Input */}
              {!appliedCoupon ? (
                <div className="space-y-2">
                  <label htmlFor="coupon" className="text-sm font-medium text-gray-700">
                    Apply Coupon Code
                  </label>
                  <div className="flex space-x-2">
                    <Input
                      id="coupon"
                      placeholder="Enter coupon code"
                      value={couponCode}
                      onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                      className="flex-1"
                    />
                    <Button 
                      onClick={handleApplyCoupon}
                      variant="outline"
                    >
                      Apply
                    </Button>
                  </div>
                  <div className="text-xs text-gray-500">
                    Try these codes: WELCOME20, SUMMER10, FESTIVE25
                  </div>
                </div>
              ) : (
                <motion.div 
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="bg-green-50 text-green-800 p-3 rounded-lg flex justify-between items-center text-sm"
                >
                  <div>
                    <span className="font-medium">{appliedCoupon}</span>
                    <span className="ml-2">({discount}% off)</span>
                  </div>
                  <button 
                    onClick={removeCoupon}
                    className="text-green-700 hover:text-green-900 underline text-xs"
                  >
                    Remove
                  </button>
                </motion.div>
              )}
              
              {/* Price Summary */}
              <div className="space-y-3 border-b pb-4">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>{formatPrice(dynamicSubtotal)}</span>
                </div>
                
                {discount > 0 && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="flex justify-between text-green-600"
                  >
                    <span>Discount</span>
                    <span>-{formatPrice(discountAmount)}</span>
                  </motion.div>
                )}
                
                <div className="flex justify-between text-gray-600">
                  <span>Shipping</span>
                  <span>{shippingFee === 0 ? "Free" : formatPrice(shippingFee)}</span>
                </div>
                
                <div className="flex justify-between text-gray-600">
                  <span>Tax (18%)</span>
                  <span>{formatPrice(taxAmount)}</span>
                </div>
              </div>
              
              {/* Total */}
              <div className="flex justify-between font-medium text-lg text-gray-900">
                <span>Total</span>
                <span>{formatPrice(totalAmount)}</span>
              </div>
              
              {/* Checkout Button */}
              <Link to="/checkout">
                <Button className="w-full h-12 text-base">
                  Proceed to Checkout
                </Button>
              </Link>
              
              {/* Payment Methods */}
              <div className="text-xs text-center text-gray-500">
                <p>We accept the following payment methods:</p>
                <div className="flex justify-center space-x-2 mt-3">
                  <div className="h-7 w-11 bg-gray-200 rounded flex items-center justify-center text-[0.65rem] font-medium">VISA</div>
                  <div className="h-7 w-11 bg-gray-200 rounded flex items-center justify-center text-[0.65rem] font-medium">MC</div>
                  <div className="h-7 w-11 bg-gray-200 rounded flex items-center justify-center text-[0.65rem] font-medium">AMEX</div>
                  <div className="h-7 w-11 bg-gray-200 rounded flex items-center justify-center text-[0.65rem] font-medium">UPI</div>
                </div>
              </div>
              
              {/* Guarantees */}
              <div className="border-t pt-4 mt-2">
                <ul className="space-y-2 text-xs text-gray-600">
                  <li className="flex items-center">
                    <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Free shipping on orders over ₹2,000
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    30-day hassle-free returns
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Secure payment processing
                  </li>
                </ul>
              </div>
            </motion.div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
