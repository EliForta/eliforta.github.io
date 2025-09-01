import React from 'react';

interface TextImageBlockProps {
  children: React.ReactNode;
  image?: {
    src: string;
    alt: string;
    position?: 'left' | 'right' | 'center';
    size?: 'small' | 'medium' | 'large';
  };
  className?: string;
}

const TextImageBlock = ({ children, image, className = '' }: TextImageBlockProps) => {
  if (!image) {
    return <div className={`prose prose-lg max-w-none ${className}`}>{children}</div>;
  }

  const imageSize = {
    small: 'w-32 h-32',
    medium: 'w-48 h-48', 
    large: 'w-64 h-64'
  }[image.size || 'medium'];

  if (image.position === 'center') {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="prose prose-lg max-w-none">{children}</div>
        <div className="flex justify-center">
          <div className={`${imageSize} relative overflow-hidden rounded-lg border border-border bg-muted/20`}>
            <img 
              src={image.src} 
              alt={image.alt}
              className="w-full h-full object-cover"
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`grid md:grid-cols-2 gap-8 items-center ${className}`}>
      {image.position === 'left' && (
        <div className={`${imageSize} mx-auto relative overflow-hidden rounded-lg border border-border bg-muted/20`}>
          <img 
            src={image.src} 
            alt={image.alt}
            className="w-full h-full object-cover"
          />
        </div>
      )}
      
      <div className="prose prose-lg max-w-none">
        {children}
      </div>
      
      {image.position === 'right' && (
        <div className={`${imageSize} mx-auto relative overflow-hidden rounded-lg border border-border bg-muted/20`}>
          <img 
            src={image.src} 
            alt={image.alt}
            className="w-full h-full object-cover"
          />
        </div>
      )}
    </div>
  );
};

export default TextImageBlock;