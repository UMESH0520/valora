import ProductCard from "@/components/ProductCard";

const items = [
  { id: "blazer-1", name: "Tailored Linen Blazer", price: 5999, image: "https://images.unsplash.com/photo-1592878849125-7d3b0c45b495?q=80&w=1600&auto=format&fit=crop", category: "Blazers" },
  { id: "blazer-2", name: "Classic Single-Breasted", price: 6499, image: "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=1600&auto=format&fit=crop", category: "Blazers" },
  { id: "blazer-3", name: "Modern Slim Fit", price: 6299, image: "https://images.unsplash.com/photo-1520975963841-56a1d8e8af1d?q=80&w=1600&auto=format&fit=crop", category: "Blazers" },
  { id: "blazer-4", name: "Double-Breasted Wool", price: 7499, image: "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?q=80&w=1600&auto=format&fit=crop", category: "Blazers" },
];

export default function Blazers() {
  return (
    <div className="section-container">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold mb-2">Blazers</h1>
        <p className="text-gray-600 max-w-2xl">Elevate your look with structured silhouettes and refined tailoring.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {items.map((p) => (
          <ProductCard key={p.id} {...p} />
        ))}
      </div>
    </div>
  );
}
