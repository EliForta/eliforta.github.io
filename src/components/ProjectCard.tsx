import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

interface ProjectCardProps {
  title: string;
  description: string;
  image: string;
  tags: string[];
  slug: string;
  year: string;
  category: string;
}

const ProjectCard = ({ title, description, image, tags, slug, year, category }: ProjectCardProps) => {
  return (
    <Card className="group relative overflow-hidden bg-card hover:shadow-lg transition-all duration-300 border-border/50">
      {/* Blueprint corner accents */}
      <div className="absolute top-2 left-2 w-4 h-4 border-l-2 border-t-2 border-primary/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      <div className="absolute bottom-2 right-2 w-4 h-4 border-r-2 border-b-2 border-primary/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      
      <div className="aspect-video overflow-hidden bg-muted">
        <img 
          src={image} 
          alt={title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
      </div>
      
      <CardHeader className="relative">
        {/* Technical label */}
        <div className="flex items-center justify-between mb-2">
          <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
            {category}
          </span>
          <span className="font-mono text-xs text-muted-foreground">
            {year}
          </span>
        </div>
        
        <CardTitle className="text-xl group-hover:text-primary transition-colors duration-300">
          {title}
        </CardTitle>
        <CardDescription className="text-muted-foreground leading-relaxed">
          {description}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="flex flex-wrap gap-2 mb-4">
          {tags.map((tag, index) => (
            <Badge 
              key={index} 
              variant="secondary" 
              className="text-xs font-mono bg-secondary/50 text-secondary-foreground hover:bg-secondary/70 transition-colors"
            >
              {tag}
            </Badge>
          ))}
        </div>
        
        <Link to={`/project/${slug}`}>
          <Button 
            variant="outline" 
            className="w-full border-primary/20 hover:bg-primary/5 hover:border-primary/40 transition-all duration-300"
          >
            View Details
            <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
};

export default ProjectCard;