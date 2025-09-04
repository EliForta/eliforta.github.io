import React from "react";

type GalleryItem = {
  src: string;
  alt?: string;
  caption?: string;
};

type GalleryProps = {
  items: GalleryItem[];
  className?: string;
};

const Gallery: React.FC<GalleryProps> = ({ items, className }) => {
  if (!items || items.length === 0) return null;

  return (
    <section className={"mt-12 " + (className ?? "")}> 
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
        <div className="w-2 h-2 bg-primary rounded-full"></div>
        Gallery
      </h2>

      {/* Masonry-style columns for mixed aspect ratios */}
      <div className="[column-fill:_balance] sm:columns-2 lg:columns-3 gap-4">
        {items.map((item, index) => (
          <figure key={index} className="mb-4 break-inside-avoid rounded-lg overflow-hidden border border-border/50 bg-muted/10">
            <img
              src={item.src}
              alt={item.alt || "Project image"}
              className="w-full h-auto object-cover transition-transform duration-500 hover:scale-[1.02]"
              loading="lazy"
            />
            {item.caption && (
              <figcaption className="px-3 py-2 text-xs text-muted-foreground border-t border-border/50 bg-background/60">
                {item.caption}
              </figcaption>
            )}
          </figure>
        ))}
      </div>
    </section>
  );
};

export type { GalleryItem };
export default Gallery;


