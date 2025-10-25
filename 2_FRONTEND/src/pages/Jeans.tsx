import ProductCard from "@/components/ProductCard";

const items = [
  { id: "jeans-1", name: "Selvedge Denim Jeans", price: 4499, image: "https://images.unsplash.com/photo-1562157873-818bc0726f68?q=80&w=1600&auto=format&fit=crop", category: "Jeans" },
  { id: "jeans-2", name: "Slim Fit Stretch Jeans", price: 3999, image: "https://images.unsplash.com/photo-1516826957135-700dedea698c?q=80&w=1600&auto=format&fit=crop", category: "Jeans" },
  { id: "jeans-3", name: "Relaxed Fit Vintage Wash", price: 4299, image: "https://images.unsplash.com/photo-1542272604-787c3835535d?q=80&w=1600&auto=format&fit=crop", category: "Jeans" },
  { id: "jeans-4", name: "High-Rise Straight", price: 4199, image: "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1600&auto=format&fit=crop", category: "Jeans" },
];

export default function Jeans() {
  return (
    <div className="section-container">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold mb-2">Jeans</h1>
        <p className="text-gray-600 max-w-2xl">Durable denim designed for movement and made to last.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {items.map((p) => (
          <ProductCard key={p.id} {...p} />
        ))}
      </div>
    </div>
  );
}
