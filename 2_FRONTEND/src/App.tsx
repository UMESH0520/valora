
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import { CartProvider } from "@/context/CartContext";
import Index from "@/pages/Index";
import NotFound from "@/pages/NotFound";
import NewArrivals from "@/pages/NewArrivals";
import Cart from "@/pages/Cart";
import Checkout from "@/pages/Checkout";
import CheckoutSuccess from "@/pages/CheckoutSuccess";
import Shop from "@/pages/Shop";
import Hoodies from "@/pages/Hoodies";
import Jeans from "@/pages/Jeans";
import Blazers from "@/pages/Blazers";
import WomenTops from "@/pages/WomenTops";
import "./App.css";

function App() {
  return (
    <CartProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/new-arrivals" element={<NewArrivals />} />
          <Route path="/shop" element={<Shop />} />
          <Route path="/hoodies" element={<Hoodies />} />
          <Route path="/jeans" element={<Jeans />} />
          <Route path="/blazers" element={<Blazers />} />
          <Route path="/women-tops" element={<WomenTops />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/checkout-success" element={<CheckoutSuccess />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
        <Toaster />
      </Router>
    </CartProvider>
  );
}

export default App;
