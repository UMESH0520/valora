import ProductCard from "@/components/ProductCard";
import { Link } from "react-router-dom";

const categories = [
  { name: "Hoodies", href: "/hoodies", image: "https://images.unsplash.com/photo-1512288094938-363287817259?q=80&w=1600&auto=format&fit=crop" },
  { name: "Jeans", href: "/jeans", image: "https://images.unsplash.com/photo-1562157873-818bc0726f68?q=80&w=1600&auto=format&fit=crop" },
  { name: "Blazers", href: "/blazers", image: "https://images.unsplash.com/photo-1592878849125-7d3b0c45b495?q=80&w=1600&auto=format&fit=crop" },
  { name: "Women Tops", href: "/women-tops", image: "https://images.unsplash.com/photo-1534187454203-3b61184c6662?q=80&w=1600&auto=format&fit=crop" },
];

const featured = [
  { id: "shop-1", name: "Cashmere Sweater", price: 3899, image: "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=1600&auto=format&fit=crop", category: "Knitwear" },
  { id: "shop-2", name: "Classic White Tee", price: 1299, image: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=1600&auto=format&fit=crop", category: "Tops" },
  { id: "shop-3", name: "Chelsea Leather Boots", price: 4999, image: "https://images.unsplash.com/photo-1638247025967-b4e38f787b76?q=80&w=1600&auto=format&fit=crop", category: "Footwear" },
  { id: "shop-4", name: "Lightweight Overcoat", price: 5999, image: "https://images.unsplash.com/photo-1541346160430-93fcee38d521?q=80&w=1600&auto=format&fit=crop", category: "Outerwear" },
];

export default function Shop() {
  return (
    <div className="section-container">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold mb-2">Shop</h1>
        <p className="text-gray-600 max-w-2xl">Browse by category or explore featured picks.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        {categories.map((c) => (
          <Link key={c.name} to={c.href} className="group relative rounded-xl overflow-hidden">
            <div className="aspect-[4/5] bg-gray-100">
              <img src={c.image} alt={c.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
            </div>
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent flex items-end p-4">
              <span className="text-white text-lg font-semibold">{c.name}</span>
            </div>
          </Link>
        ))}
      </div>

      <h2 className="text-2xl font-semibold mb-4">Featured</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {featured.map((p) => (
          <ProductCard key={p.id} {...p} />
        ))}
      </div>
    </div>
  );
}
