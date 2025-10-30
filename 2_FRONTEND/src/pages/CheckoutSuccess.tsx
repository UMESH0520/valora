
import { useEffect } from "react";
import { Link } from "react-router-dom";
import { CheckCircle, Home, ShoppingBag } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function CheckoutSuccess() {
  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="section-container min-h-[70vh] flex flex-col items-center justify-center py-12">
      <div className="max-w-lg w-full text-center space-y-6">
        <div className="inline-flex h-24 w-24 items-center justify-center rounded-full bg-green-100 text-green-500 mx-auto">
          <CheckCircle className="h-12 w-12" />
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900">Order Placed Successfully!</h1>
        
        <p className="text-gray-600">
          Thank you for your purchase. Your order has been received and is now being processed. 
          We'll send you a confirmation email with your order details shortly.
        </p>
        
        <div className="bg-gray-50 rounded-lg p-6 text-left">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Order Information</h2>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Order Number:</span>
              <span className="font-medium">#INV-{Math.floor(100000 + Math.random() * 900000)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-500">Date:</span>
              <span className="font-medium">{new Date().toLocaleDateString('en-IN', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-500">Payment Method:</span>
              <span className="font-medium">Razorpay</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-500">Shipping Method:</span>
              <span className="font-medium">Standard Delivery (3-5 business days)</span>
            </div>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 pt-4">
          <Link to="/" className="flex-1">
            <Button variant="outline" className="w-full gap-2">
              <Home className="h-4 w-4" />
              Return Home
            </Button>
          </Link>
          
          <Link to="/new-arrivals" className="flex-1">
            <Button className="w-full gap-2">
              <ShoppingBag className="h-4 w-4" />
              Continue Shopping
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
