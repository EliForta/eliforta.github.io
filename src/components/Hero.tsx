import { Button } from "@/components/ui/button";

const Hero = () => {
  return (
    <section className="relative min-h-[80vh] flex items-center justify-center blueprint-grid">
      {/* Background technical decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-20 h-20 border border-primary/20 rotate-45"></div>
        <div className="absolute bottom-20 right-10 w-16 h-16 border border-technical-orange/20"></div>
        <div className="absolute top-1/2 left-1/4 w-2 h-2 bg-primary/30 rounded-full"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-technical-coral/40 rounded-full"></div>
      </div>
      
      <div className="container mx-auto px-6 text-center relative z-10">
        <div className="max-w-4xl mx-auto">
          {/* Technical label */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-muted/50 border border-border mb-6">
            <span className="w-2 h-2 bg-primary rounded-full"></span>
            <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
              Mechanical Engineering Student
            </span>
          </div>
          
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 tracking-tight">
            Eli
            <span className="block text-primary relative">
              Forta
              {/* Blueprint line decoration */}
              <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-24 h-0.5 bg-primary/30"></div>
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-8 leading-relaxed">
            
          </p>
          
          <div className="flex justify-center">
            <Button 
              size="lg" 
              onClick={() => document.getElementById('projects')?.scrollIntoView({ behavior: 'smooth' })}
              className="tech-corners px-8 py-3 bg-primary hover:bg-primary/90 text-primary-foreground font-medium"
            >
              View Projects
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
