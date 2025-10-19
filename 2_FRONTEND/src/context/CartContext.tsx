
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useToast } from "@/hooks/use-toast";

export type CartItem = {
  id: string;
  name: string;
  price: number;
  image: string;
  quantity: number;
  size?: string;
};

type CartContextType = {
  items: CartItem[];
  addItem: (item: Omit<CartItem, "quantity"> & { quantity?: number; size?: string }) => void;
  removeItem: (id: string, size?: string) => void;
  updateQuantity: (id: string, quantity: number, size?: string) => void;
  clearCart: () => void;
  totalItems: number;
  subtotal: number;
  appliedCoupon: string | null;
  discount: number;
  applyCoupon: (code: string) => boolean;
  removeCoupon: () => void;
};

const CartContext = createContext<CartContextType | undefined>(undefined);

// Available coupon codes with their discount percentages
const VALID_COUPONS: Record<string, number> = {
  "WELCOME20": 20,
  "SUMMER10": 10,
  "FESTIVE25": 25,
};

export const CartProvider = ({ children }: { children: ReactNode }) => {
  const { toast } = useToast();
  const [items, setItems] = useState<CartItem[]>([]);
  const [appliedCoupon, setAppliedCoupon] = useState<string | null>(null);
  const [discount, setDiscount] = useState(0);

  // Load cart from localStorage on mount
  useEffect(() => {
    const savedCart = localStorage.getItem("cart");
    const savedCoupon = localStorage.getItem("coupon");
    
    if (savedCart) {
      try {
        setItems(JSON.parse(savedCart));
      } catch (e) {
        console.error("Failed to parse cart from localStorage", e);
      }
    }
    
    if (savedCoupon) {
      setAppliedCoupon(savedCoupon);
      if (VALID_COUPONS[savedCoupon]) {
        setDiscount(VALID_COUPONS[savedCoupon]);
      }
    }
  }, []);

  // Save cart to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("cart", JSON.stringify(items));
    
    if (appliedCoupon) {
      localStorage.setItem("coupon", appliedCoupon);
    } else {
      localStorage.removeItem("coupon");
    }
  }, [items, appliedCoupon]);

  const addItem = (item: Omit<CartItem, "quantity"> & { quantity?: number; size?: string }) => {
    const quantity = item.quantity || 1;
    
    setItems(prevItems => {
      // Check if the item with the same ID and size already exists
      const existingItemIndex = prevItems.findIndex(
        i => i.id === item.id && (!item.size || i.size === item.size)
      );
      
      if (existingItemIndex !== -1) {
        // Update the quantity of the existing item
        const updatedItems = [...prevItems];
        updatedItems[existingItemIndex] = {
          ...updatedItems[existingItemIndex],
          quantity: updatedItems[existingItemIndex].quantity + quantity
        };
        
        toast({
          title: "Item updated in cart",
          description: `Quantity increased to ${updatedItems[existingItemIndex].quantity}`,
        });
        
        return updatedItems;
      } else {
        // Add the new item to the cart
        toast({
          title: "Item added to cart",
          description: `${item.name} added to your cart`,
        });
        
        return [...prevItems, { ...item, quantity }];
      }
    });
  };

  const removeItem = (id: string, size?: string) => {
    setItems(prevItems => {
      const newItems = prevItems.filter(item => 
        !(item.id === id && (!size || item.size === size))
      );
      
      toast({
        title: "Item removed",
        description: "The item has been removed from your cart",
      });
      
      return newItems;
    });
  };

  const updateQuantity = (id: string, quantity: number, size?: string) => {
    if (quantity < 1) {
      removeItem(id, size);
      return;
    }
    
    setItems(prevItems => prevItems.map(item => 
      (item.id === id && (!size || item.size === size))
        ? { ...item, quantity }
        : item
    ));
  };

  const clearCart = () => {
    setItems([]);
    setAppliedCoupon(null);
    setDiscount(0);
    localStorage.removeItem("cart");
    localStorage.removeItem("coupon");
  };
  
  const applyCoupon = (code: string) => {
    const upperCode = code.toUpperCase();
    if (VALID_COUPONS[upperCode]) {
      setAppliedCoupon(upperCode);
      setDiscount(VALID_COUPONS[upperCode]);
      
      toast({
        title: "Coupon applied",
        description: `${upperCode} coupon applied successfully`,
      });
      
      return true;
    } else {
      toast({
        title: "Invalid coupon",
        description: "The coupon code you entered is invalid",
        variant: "destructive",
      });
      
      return false;
    }
  };
  
  const removeCoupon = () => {
    setAppliedCoupon(null);
    setDiscount(0);
    localStorage.removeItem("coupon");
    
    toast({
      title: "Coupon removed",
      description: "The coupon has been removed from your cart",
    });
  };

  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
  const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <CartContext.Provider value={{
      items,
      addItem,
      removeItem,
      updateQuantity,
      clearCart,
      totalItems,
      subtotal,
      appliedCoupon,
      discount,
      applyCoupon,
      removeCoupon,
    }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
};
