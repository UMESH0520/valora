import ProductCard from "@/components/ProductCard";

const items = [
  { id: "hoodie-1", name: "Classic Fleece Hoodie", price: 2999, image: "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=1600&auto=format&fit=crop", category: "Hoodies" },
  { id: "hoodie-2", name: "Oversized Street Hoodie", price: 3499, image: "https://images.unsplash.com/photo-1503342217505-b0a15cf70489?q=80&w=1600&auto=format&fit=crop", category: "Hoodies" },
  { id: "hoodie-3", name: "Zip-Up Tech Hoodie", price: 3799, image: "https://images.unsplash.com/photo-1512288094938-363287817259?q=80&w=1600&auto=format&fit=crop", category: "Hoodies" },
  { id: "hoodie-4", name: "Minimalist Pullover", price: 2899, image: "https://images.unsplash.com/photo-1484515991647-c5760fcecfc7?q=80&w=1600&auto=format&fit=crop", category: "Hoodies" },
];

export default function Hoodies() {
  return (
    <div className="section-container">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold mb-2">Hoodies</h1>
        <p className="text-gray-600 max-w-2xl">Comfort-first hoodies designed with premium fabrics and clean lines.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {items.map((p) => (
          <ProductCard key={p.id} {...p} />
        ))}
      </div>
    </div>
  );
}
