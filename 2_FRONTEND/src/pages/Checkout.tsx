
import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useCart } from "@/context/CartContext";
import { useToast } from "@/hooks/use-toast";
import { loadRazorpayScript, initiateRazorpayPayment } from "@/lib/razorpay";
import { User, CreditCard, MapPin, ChevronRight, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { useLivePricesMap } from "@/hooks/useLivePrice";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

// Form validation schema
const formSchema = z.object({
  firstName: z.string().min(2, "First name must be at least 2 characters"),
  lastName: z.string().min(2, "Last name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  phone: z.string().min(10, "Phone number must be at least 10 digits"),
  address: z.string().min(5, "Address must be at least 5 characters"),
  city: z.string().min(2, "City must be at least 2 characters"),
  state: z.string().min(2, "State must be at least 2 characters"),
  pincode: z.string().min(6, "Pincode must be at least 6 characters"),
});

export default function Checkout() {
  const { 
    items, 
    subtotal, 
    appliedCoupon, 
    discount, 
    clearCart
  } = useCart();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentStep, setPaymentStep] = useState(1);
  
  // Form setup
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      firstName: "",
      lastName: "",
      email: "",
      phone: "",
      address: "",
      city: "",
      state: "",
      pincode: "",
    },
  });

  // Live prices map (rupees) -> convert to paise
  const livePrices = useLivePricesMap(items.map(i => i.id))
  const dynamicSubtotal = useMemo(() => {
    return items.reduce((sum, item) => {
      const liveRupees = livePrices[item.id]
      const unitPaise = typeof liveRupees === 'number' ? Math.round(liveRupees * 100) : item.price
      return sum + unitPaise * item.quantity
    }, 0)
  }, [items, livePrices])

  // Calculate final amounts
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

  // Handle form submission
  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setPaymentStep(2);
    console.log("Form values:", values);
  };

  // Redirect to cart if cart is empty
  useEffect(() => {
    if (items.length === 0) {
      navigate("/cart");
    }
  }, [items, navigate]);

  // Handle payment processing
  const handlePayment = async () => {
    setIsProcessing(true);
    
    try {
      // Load Razorpay script
      const scriptLoaded = await loadRazorpayScript();
      
      if (!scriptLoaded) {
        toast({
          title: "Payment Failed",
          description: "Could not load payment gateway. Please try again.",
          variant: "destructive",
        });
        setIsProcessing(false);
        return;
      }
      
      // Customer information from form
      const { firstName, lastName, email, phone } = form.getValues();
      
      // Initialize payment
      initiateRazorpayPayment({
        key: "rzp_test_YourTestKey", // Replace with your actual test key
        amount: totalAmount,
        currency: "INR",
        name: "VALORA",
        description: "Purchase from VALORA Fashion Store",
        prefill: {
          name: `${firstName} ${lastName}`,
          email: email,
          contact: phone,
        },
        notes: {
          address: form.getValues().address,
        },
        theme: {
          color: "#000000",
        },
        handler: function(response) {
          // Handle successful payment
          toast({
            title: "Payment Successful!",
            description: `Payment ID: ${response.razorpay_payment_id}`,
          });
          
          // Clear cart and redirect to success page
          clearCart();
          navigate("/checkout-success");
        }
      });
    } catch (error) {
      console.error("Payment error:", error);
      toast({
        title: "Payment Failed",
        description: "An error occurred during payment processing. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="section-container mb-16">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-semibold">Checkout</h1>
        <Link to="/cart" className="flex items-center text-sm text-gray-600 hover:text-primary">
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Cart
        </Link>
      </div>

      {/* Checkout Steps */}
      <div className="mb-10">
        <div className="flex items-center">
          <div className={`flex flex-col items-center ${paymentStep === 1 ? 'text-primary' : 'text-gray-500'}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center mb-1 ${paymentStep === 1 ? 'bg-primary text-white' : 'bg-gray-200'}`}>
              <User className="w-5 h-5" />
            </div>
            <span className="text-xs">Details</span>
          </div>
          
          <div className={`flex-1 h-1 mx-2 ${paymentStep >= 1 ? 'bg-primary' : 'bg-gray-200'}`}></div>
          
          <div className={`flex flex-col items-center ${paymentStep === 2 ? 'text-primary' : 'text-gray-500'}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center mb-1 ${paymentStep === 2 ? 'bg-primary text-white' : 'bg-gray-200'}`}>
              <CreditCard className="w-5 h-5" />
            </div>
            <span className="text-xs">Payment</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Checkout Form - Left Side */}
        <div className="lg:col-span-2">
          {paymentStep === 1 && (
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-medium mb-6 flex items-center">
                <MapPin className="mr-2 h-5 w-5 text-primary" />
                Shipping Information
              </h2>
              
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="firstName"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>First Name</FormLabel>
                          <FormControl>
                            <Input placeholder="John" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="lastName"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Last Name</FormLabel>
                          <FormControl>
                            <Input placeholder="Doe" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email</FormLabel>
                          <FormControl>
                            <Input placeholder="john.doe@example.com" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="phone"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Phone Number</FormLabel>
                          <FormControl>
                            <Input placeholder="9876543210" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  
                  <FormField
                    control={form.control}
                    name="address"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Address</FormLabel>
                        <FormControl>
                          <Input placeholder="123 Main Street, Apartment 4B" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <FormField
                      control={form.control}
                      name="city"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>City</FormLabel>
                          <FormControl>
                            <Input placeholder="Mumbai" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="state"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>State</FormLabel>
                          <FormControl>
                            <Input placeholder="Maharashtra" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="pincode"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Pincode</FormLabel>
                          <FormControl>
                            <Input placeholder="400001" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  
                  <Button type="submit" className="w-full">
                    Continue to Payment
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Button>
                </form>
              </Form>
            </div>
          )}
          
          {paymentStep === 2 && (
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-medium mb-6 flex items-center">
                <CreditCard className="mr-2 h-5 w-5 text-primary" />
                Payment Information
              </h2>
              
              <div className="space-y-6">
                <div className="bg-gray-50 p-4 rounded-md">
                  <h3 className="font-medium mb-3">Shipping Address</h3>
                  <p className="text-sm text-gray-600">
                    {form.getValues().firstName} {form.getValues().lastName}<br />
                    {form.getValues().address}<br />
                    {form.getValues().city}, {form.getValues().state} {form.getValues().pincode}<br />
                    {form.getValues().phone}<br />
                    {form.getValues().email}
                  </p>
                </div>
                
                <div className="border-t pt-6">
                  <h3 className="font-medium mb-3">Payment Method</h3>
                  <div className="bg-white border rounded-md p-4">
                    <div className="flex items-center">
                      <div className="w-10 h-6 bg-gray-200 rounded flex items-center justify-center text-[0.65rem] font-medium">
                        <img 
                          src="https://razorpay.com/build/browser/static/razorpay-logo.5cdb58df.svg" 
                          alt="Razorpay" 
                          className="h-4 w-auto" 
                        />
                      </div>
                      <span className="ml-3 text-sm font-medium">Razorpay Secure Checkout</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      You'll be redirected to Razorpay's secure payment gateway to complete your purchase.
                    </p>
                  </div>
                </div>
                
                <div className="flex space-x-4">
                  <Button 
                    variant="outline" 
                    onClick={() => setPaymentStep(1)}
                    className="flex-1"
                  >
                    Back to Details
                  </Button>
                  
                  <Button 
                    className="flex-1"
                    disabled={isProcessing}
                    onClick={handlePayment}
                  >
                    {isProcessing ? "Processing..." : `Pay ${formatPrice(totalAmount)}`}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Order Summary - Right Side */}
        <div className="lg:col-span-1">
          <div className="bg-gray-50 rounded-lg p-6 sticky top-8">
            <h2 className="text-xl font-medium text-gray-900 mb-4">Order Summary</h2>
            
            <div className="space-y-4 max-h-80 overflow-auto pr-2 mb-4">
              {items.map((item) => (
                <div key={`${item.id}-${item.size || 'default'}`} className="flex items-start border-b pb-4">
                  <div className="h-16 w-12 bg-gray-100 rounded overflow-hidden flex-shrink-0">
                    <img 
                      src={item.image} 
                      alt={item.name} 
                      className="h-full w-full object-cover"
                    />
                  </div>
                  <div className="ml-4 flex-1">
                    <div className="flex justify-between">
                      <p className="text-sm font-medium">{item.name}</p>
                      <p className="text-sm font-medium">{(() => { const liveRupees = livePrices[item.id]; const unitPaise = typeof liveRupees === 'number' ? Math.round(liveRupees * 100) : item.price; return formatPrice(unitPaise * item.quantity) })()}</p>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <p>{item.size && `Size: ${item.size}`} · Qty: {item.quantity}</p>
                      <p>{(() => { const liveRupees = livePrices[item.id]; const unitPaise = typeof liveRupees === 'number' ? Math.round(liveRupees * 100) : item.price; return formatPrice(unitPaise) })()} each</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Price Summary */}
            <div className="space-y-2 border-b pb-4">
              <div className="flex justify-between text-gray-600">
                <span>Subtotal</span>
                <span>{formatPrice(dynamicSubtotal)}</span>
              </div>
              
              {discount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Discount {appliedCoupon && `(${appliedCoupon})`}</span>
                  <span>-{formatPrice(discountAmount)}</span>
                </div>
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
            <div className="flex justify-between font-medium text-lg text-gray-900 mt-4">
              <span>Total</span>
              <span>{formatPrice(totalAmount)}</span>
            </div>
            
            {/* Delivery note */}
            <div className="mt-6 text-sm text-gray-500 bg-gray-100 p-3 rounded-md">
              <p>
                Standard delivery: 3-5 business days<br />
                Free shipping on orders over ₹2,000
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
