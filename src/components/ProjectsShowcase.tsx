import ProjectCard from "./ProjectCard";
import dispenserImage from "@/assets/clipboard-hero.gif";
import energyImage from "@/assets/energy-storage-project.jpg";
import jigImage from "@/assets/manufacturing-jig-project.jpg";

// Sample project data - in a real implementation, this would come from a CMS or API
const projects = [
  {
    title: "Accessible Clipboard Dispenser",
    description: "Designed and prototyped a automatic clipboard dispensor for volunteers with disabilities.",
    image: dispenserImage,
    tags: ["CAD Design", "Prototyping", "3D Printing", "Programming", "CNC Machining"],
    slug: "clipboard-dispenser",
    year: "January 2025 - May 2025",
    category: ""
  },
  {
    title: "Sustainable Energy Storage",
    description: "Developed a mechanical energy storage system using flywheel technology for renewable energy applications.",
    image: energyImage,
    tags: ["Mechanical Design", "Energy Systems", "SolidWorks", "FEA Analysis"],
    slug: "energy-storage-flywheel",
    year: "2023",
    category: ""
  }
];

const ProjectsShowcase = () => {
  return (
    <section id="projects" className="py-20 relative">
      <div className="container mx-auto px-6">
        {/* Section header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-muted/50 border border-border mb-4">
            <span className="w-2 h-2 bg-primary rounded-full"></span>
            <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
              Featured Work
            </span>
          </div>
          
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Engineering Projects
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            A collection of mechanical engineering projects showcasing innovation in design, 
            analysis, and problem-solving across various domains.
          </p>
          
          {/* Blueprint accent line */}
          <div className="mt-8 flex justify-center">
            <div className="w-24 h-0.5 bg-primary/30 relative">
              <div className="absolute -left-2 -right-2 h-0.5 bg-primary/10"></div>
            </div>
          </div>
        </div>
        
        {/* Projects grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {projects.map((project, index) => (
            <ProjectCard
              key={index}
              title={project.title}
              description={project.description}
              image={project.image}
              tags={project.tags}
              slug={project.slug}
              year={project.year}
              category={project.category}
            />
          ))}
        </div>
        
        {/* View all projects */}
        <div className="text-center mt-12">
          <p className="text-muted-foreground mb-4">
            More projects coming soon...
          </p>
          <div className="inline-flex items-center gap-2 text-sm text-primary">
            <span className="w-1 h-1 bg-primary rounded-full animate-pulse"></span>
            Currently developing new prototypes
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProjectsShowcase;
