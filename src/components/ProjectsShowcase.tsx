import ProjectCard from "./ProjectCard";
import droneImage from "@/assets/drone-landing-project.jpg";
import energyImage from "@/assets/energy-storage-project.jpg";
import jigImage from "@/assets/manufacturing-jig-project.jpg";

// Sample project data - in a real implementation, this would come from a CMS or API
const projects = [
  {
    title: "Autonomous Drone Landing System",
    description: "Designed and prototyped a precision landing mechanism for commercial drones using servo motors and computer vision integration.",
    image: droneImage,
    tags: ["CAD Design", "Prototyping", "Servo Systems", "Computer Vision"],
    slug: "autonomous-drone-landing",
    year: "2024",
    category: "Robotics"
  },
  {
    title: "Sustainable Energy Storage",
    description: "Developed a mechanical energy storage system using flywheel technology for renewable energy applications.",
    image: energyImage,
    tags: ["Mechanical Design", "Energy Systems", "SolidWorks", "FEA Analysis"],
    slug: "energy-storage-flywheel",
    year: "2023",
    category: "Energy Systems"
  },
  {
    title: "Precision Manufacturing Jig",
    description: "Created custom manufacturing fixtures to improve production accuracy and reduce setup time by 40%.",
    image: jigImage,
    tags: ["Manufacturing", "Precision Tools", "CNC", "Quality Control"],
    slug: "manufacturing-jig",
    year: "2023",
    category: "Manufacturing"
  },
  {
    title: "Biomechanical Prosthetic Hand",
    description: "Engineered a low-cost prosthetic hand mechanism with improved grip strength and dexterity for developing markets.",
    image: "/api/placeholder/400/250",
    tags: ["Biomechanics", "3D Printing", "Mechanism Design", "Medical Device"],
    slug: "prosthetic-hand",
    year: "2024",
    category: "Biomedical"
  },
  {
    title: "Thermal Management System",
    description: "Designed cooling solution for high-performance computing using heat pipes and optimized fin geometry.",
    image: "/api/placeholder/400/250",
    tags: ["Thermal Analysis", "Heat Transfer", "ANSYS", "Optimization"],
    slug: "thermal-management",
    year: "2023",
    category: "Thermal Systems"
  },
  {
    title: "Automated Assembly Line",
    description: "Developed conveyor system with pneumatic actuators and PLC control for small-scale production automation.",
    image: "/api/placeholder/400/250",
    tags: ["Automation", "PLC Programming", "Pneumatics", "Industrial Design"],
    slug: "assembly-line",
    year: "2024",
    category: "Automation"
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