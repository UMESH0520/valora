import ProductCard from "@/components/ProductCard";

const items = [
  { id: "wt-1", name: "Ribbed Knit Top", price: 1999, image: "https://images.unsplash.com/photo-1534187454203-3b61184c6662?q=80&w=1600&auto=format&fit=crop", category: "Women Tops" },
  { id: "wt-2", name: "Silk Camisole", price: 2499, image: "https://images.unsplash.com/photo-1520975963841-56a1d8e8af1d?q=80&w=1600&auto=format&fit=crop", category: "Women Tops" },
  { id: "wt-3", name: "Oversized Cotton Shirt", price: 2299, image: "https://images.unsplash.com/photo-1520975916090-3105956dac38?q=80&w=1600&auto=format&fit=crop", category: "Women Tops" },
  { id: "wt-4", name: "Puff Sleeve Blouse", price: 2199, image: "https://images.unsplash.com/photo-1548142813-c348350df52b?q=80&w=1600&auto=format&fit=crop", category: "Women Tops" },
];

export default function WomenTops() {
  return (
    <div className="section-container">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold mb-2">Women Tops</h1>
        <p className="text-gray-600 max-w-2xl">Seasonal tops crafted for effortless styling and comfort.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {items.map((p) => (
          <ProductCard key={p.id} {...p} />
        ))}
      </div>
    </div>
  );
}
