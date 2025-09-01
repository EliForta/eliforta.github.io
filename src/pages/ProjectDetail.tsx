import { useParams, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Header from "@/components/Header";

import dispenserImage from "@/assets/dispenser-hero.gif";
// import energyImage from "@/assets/energy-storage-project.jpg";
// import jigImage from "@/assets/manufacturing-jig-project.jpg";

// Sample project data - in a real implementation, this would come from a CMS or API
const projectData = {
  'clipboard-dispenser': {
    title: "Accessible Clipboard Dispenser",
    category: "",
    year: "January 2025 - May 2025",
    duration: "4 months",
    team: "Team Lead",
    status: "Completed",
    description: "Designed and prototyped a automatic clipboard dispensor for volunteers with disabilities.",
    challenge: "The main challenge was designing a device that was intuitive and accessible for users with a wide range of severe disabilities, making the difficult fine motor task of picking up a clipboard simple. A second challenge arose when we discovered another team was developing a different solution for the same station. We decided to proactively collaborate with them, redesigning our dispenser to ensure our projects would be fully integrated and compatible.",
    solution: "Developed a clipboard dispenser that automatically provides a single clipboard at the push of a large, easily accessible button. The design was created using OnShape, with parts fabricated using a CNC router and a 3D printer, and the device was programmed using Arduino/C++. Throughout the development process, we worked closely with the charity to gather feedback and refine multiple prototypes, resulting in a final product that was more engaging and allowed for faster participation at the station.",
    technologies: ["CAD", "Arduino", "CNC Machining", "Servo Control", "3D Printing", "Prototyping"],
    features: [
      "Single button operation",
      "Simple, 4 step setup",
      "Rechargeable via USB-C",
      "Automatic inactivity light dimming to extend battery life",
      "User replacable front spacer to accomodate different clipboards"
    ],
    results: [
      "50% increase in user engagement",
      "Dramatically lowered time to complete station"
    ],
    images: [
     dispenserImage
    ]
  },
  'energy-storage-flywheel': {
    title: "Sustainable Energy Storage",
    category: "Energy Systems",
    year: "2023",
    duration: "8 months",
    team: "Team of 3",
    status: "Prototype Complete",
    description: "Developed a mechanical energy storage system using flywheel technology for renewable energy applications. The system stores kinetic energy during peak production and releases it during demand periods.",
    challenge: "Renewable energy sources like solar and wind are intermittent, requiring efficient storage solutions that don't rely on expensive batteries or rare earth materials.",
    solution: "Designed a high-speed flywheel system with magnetic bearings and carbon fiber rotor assembly to minimize friction losses and maximize energy density.",
    technologies: ["ANSYS", "SolidWorks", "FEA Analysis", "Composite Materials", "Magnetic Bearings", "Control Systems"],
    features: [
      "95% round-trip efficiency",
      "50,000+ charge cycles",
      "Carbon fiber rotor design",
      "Magnetic levitation bearings",
      "Integrated power electronics"
    ],
    results: [
      "Successfully demonstrated 10kWh storage capacity",
      "Achieved 95% energy conversion efficiency",
      "Cost reduction of 30% compared to battery systems",
      "Published research in engineering journal"
    ],
    images: [
   //   energyImage
    ]
  }
};

const ProjectDetail = () => {
  const { slug } = useParams<{ slug: string }>();
  
  if (!slug || !projectData[slug as keyof typeof projectData]) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="container mx-auto px-6 py-20 text-center">
          <h1 className="text-4xl font-bold mb-4">Project Not Found</h1>
          <p className="text-muted-foreground mb-8">The project you're looking for doesn't exist, or has not been completely added yet.</p>
          <Link to="/">
            <Button>Return Home</Button>
          </Link>
        </div>
      </div>
    );
  }

  const project = projectData[slug as keyof typeof projectData];

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="py-20">
        <div className="container mx-auto px-6">
          {/* Back navigation */}
          <Link 
            to="/" 
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-8"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Projects
          </Link>

          <div className="max-w-4xl mx-auto">
            {/* Project header */}
            <div className="mb-12">
              <div className="flex items-center gap-4 mb-4">
                <Badge variant="secondary" className="font-mono text-xs">
                  {project.category}
                </Badge>
                <span className="text-muted-foreground">•</span>
                <span className="font-mono text-sm text-muted-foreground">{project.year}</span>
              </div>
              
              <h1 className="text-4xl md:text-5xl font-bold mb-6 relative">
                {project.title}
                <div className="absolute -bottom-2 left-0 w-24 h-0.5 bg-primary/30"></div>
              </h1>
              
              <p className="text-lg text-muted-foreground leading-relaxed max-w-3xl">
                {project.description}
              </p>
            </div>

            {/* Project image */}
            <div className="mb-12">
              <div className="aspect-video bg-muted rounded-lg overflow-hidden border border-border/50 relative group">
                <img 
                  src={project.images[0]} 
                  alt={project.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                {/* Blueprint overlay decoration */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
            </div>

            {/* Project details grid */}
            <div className="grid md:grid-cols-3 gap-8 mb-12">
              <div className="md:col-span-2 space-y-8">
                {/* Challenge */}
                <section>
                  <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                    Challenge
                  </h2>
                  <p className="text-muted-foreground leading-relaxed">
                    {project.challenge}
                  </p>
                </section>

                {/* Solution */}
                <section>
                  <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
                    <div className="w-2 h-2 bg-technical-orange rounded-full"></div>
                    Solution
                  </h2>
                  <p className="text-muted-foreground leading-relaxed">
                    {project.solution}
                  </p>
                </section>

                {/* Key Features */}
                <section>
                  <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
                    <div className="w-2 h-2 bg-accent rounded-full"></div>
                    Key Features
                  </h2>
                  <ul className="space-y-3">
                    {project.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-muted-foreground">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </section>

                {/* Results */}
                <section>
                  <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
                    <div className="w-2 h-2 bg-technical-coral rounded-full"></div>
                    Results & Impact
                  </h2>
                  <ul className="space-y-3">
                    {project.results.map((result, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-muted-foreground">{result}</span>
                      </li>
                    ))}
                  </ul>
                </section>
              </div>

              {/* Project sidebar */}
              <div className="space-y-6">
                {/* Project info */}
                <div className="bg-muted/20 p-6 rounded-lg border border-border/50">
                  <h3 className="font-bold mb-4">Project Info</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Duration:</span>
                      <span className="font-mono">{project.duration}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Team:</span>
                      <span className="font-mono">{project.team}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Status:</span>
                      <Badge variant="secondary" className="font-mono text-xs">
                        {project.status}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Technologies */}
                <div className="bg-muted/20 p-6 rounded-lg border border-border/50">
                  <h3 className="font-bold mb-4">Technologies Used</h3>
                  <div className="flex flex-wrap gap-2">
                    {project.technologies.map((tech, index) => (
                      <Badge 
                        key={index} 
                        variant="outline" 
                        className="text-xs font-mono border-primary/20"
                      >
                        {tech}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Next project navigation */}
            <div className="border-t border-border pt-8">
              <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                <Link to="/">
                  <Button variant="outline">
                    <svg className="mr-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    All Projects
                  </Button>
                </Link>
                
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">
                    
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ProjectDetail;
