
import ProductCard from "@/components/ProductCard";

export default function NewArrivals() {
  // Pink dress product data
  const pinkDress = {
    id: "pink-high-low-dress",
    name: "Elegant High-Low Satin Dress in Blush Pink",
    price: 1999,  // Keeping the same price value, it will be formatted as INR
    image: "/lovable-uploads/6cdafd3c-63c8-411e-a40c-93b3e5acbf29.png",
    images: [
      "/lovable-uploads/f52e5d56-e721-493d-be87-0f5eec804829.png",
      "/lovable-uploads/dc653d86-3d4c-4b75-a1b8-ca6bd9a54df8.png",
      "/lovable-uploads/2d9ef997-0cab-4e1f-be0e-5d2bf2a53cc5.png",
      "/lovable-uploads/c494266c-b9bf-4206-a26a-d478fc26d1c9.png",
      "/lovable-uploads/c0eaefd2-1f20-4de7-993b-b36e8a790599.png"
    ],
    description: `
      <p>Make a statement at your next special event with our stunning High-Low Satin Dress in Blush Pink. This exquisite dress combines elegance and modern style with its graceful silhouette and premium satin finish.</p>
      
      <p><strong>Key Features:</strong></p>
      <ul>
        <li>Luxurious satin fabric with a subtle sheen</li>
        <li>Flattering high-low hemline that creates dramatic movement</li>
        <li>Sleek sleeveless design with a modest round neckline</li>
        <li>Elegant V-cut back with hidden zipper closure</li>
        <li>Structured pleats that add volume and dimension</li>
        <li>Soft blush pink color perfect for formal events, weddings, and special occasions</li>
      </ul>
      
      <p><strong>Available Sizes:</strong> Small (S), Medium (M), Large (L)</p>
      
      <p><strong>Styling Tips:</strong></p>
      <p>Pair this stunning piece with delicate heels and minimal jewelry to let the dress make the statement. Perfect for bridesmaids, formal events, galas, or any occasion where you want to make a lasting impression.</p>
      
      <p><strong>Care Instructions:</strong></p>
      <p>Dry clean only. Store on a padded hanger to maintain the shape and structure of this premium garment.</p>
    `,
    sizes: ["S", "M", "L"],
    isNew: true,
    category: "Dresses",
  };

  // Burgundy maxi dress product data
  const burgundyDress = {
    id: "burgundy-chiffon-maxi-dress",
    name: "Flowing Chiffon Maxi Dress with Sequin Belt in Burgundy",
    price: 1559, // Price in INR
    image: "/lovable-uploads/2699a1f6-cf46-49df-ba58-d8b2d6fcb21a.png",
    images: [
      "/lovable-uploads/2aeeb1bd-177c-45e6-af22-437e5ade9b00.png",
      "/lovable-uploads/66b7946c-0144-41ce-abd3-11e15db024d8.png",
      "/lovable-uploads/5753943f-8466-466f-867f-b89a0450a9f5.png",
      "/lovable-uploads/e9c732df-7995-4465-a69a-fc6ce2b4d41f.png",
      "/lovable-uploads/4a0b51aa-9d3a-40a4-86a5-401200087c4e.png"
    ],
    description: `
      <p>Elevate your evening wardrobe with our breathtaking Flowing Chiffon Maxi Dress in rich burgundy. This stunning floor-length gown combines timeless elegance with modern details for a look that commands attention at any special occasion.</p>
      
      <p><strong>Key Features:</strong></p>
      <ul>
        <li>Premium lightweight chiffon fabric that creates ethereal movement</li>
        <li>Elegant V-neckline with fluttery cap sleeves for a feminine touch</li>
        <li>Glamorous black sequin belt that defines the waist and adds sparkle</li>
        <li>Flowing A-line silhouette with practical hidden side pockets</li>
        <li>Graceful high-low hem with a subtle train effect</li>
        <li>Concealed back zipper for a sleek, seamless finish</li>
        <li>Rich burgundy color perfect for evening events, weddings, and formal occasions</li>
      </ul>
      
      <p><strong>Available Sizes:</strong> Extra Small (XS), Small (S), Medium (M), Large (L), Extra Large (XL)</p>
      
      <p><strong>Styling Tips:</strong></p>
      <p>Pair this stunning gown with metallic or crystal-embellished sandals and statement earrings for maximum impact. The versatile design works beautifully for black-tie events, wedding guest attire, or elegant dinner parties. The practical pockets allow you to keep essentials close while maintaining the dress's elegant silhouette.</p>
      
      <p><strong>Care Instructions:</strong></p>
      <p>Dry clean only. To preserve the beauty of the sequin belt, store flat or on a padded hanger and avoid contact with rough surfaces.</p>
    `,
    sizes: ["XS", "S", "M", "L", "XL"],
    isNew: true,
    category: "Dresses",
  };

  return (
    <div className="section-container">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold mb-2">New Arrivals</h1>
        <p className="text-gray-600 max-w-2xl">Discover our latest additions to the collection. Fresh styles that blend timeless elegance with contemporary trends.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ProductCard {...burgundyDress} />
        <ProductCard {...pinkDress} />
        {/* Additional product cards can be added here as they arrive */}
      </div>
    </div>
  );
}
