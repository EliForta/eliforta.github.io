
import { useParams, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Header from "@/components/Header";
import Gallery from "@/components/Gallery";

import dispenserDrawing from "@/assets/clipboardDrawing.png";

import dispenserImage from "@/assets/clipboard-hero.gif";
import beamImage from "@/assets/beam-hero.jpg";
import clipboardCode from "@/assets/clipboardCode.png";
import clipboardEarlyWiring from "@/assets/clipboardEarlyWiring.jpeg";
import beamTest from "@/assets/beamTest.png";
import clipboardInterier from "@/assets/clipboardInterier.jpeg";
import clipboardSides from "@/assets/clipboardSides.jpeg";
import clipboardFinalWiring from "@/assets/clipboardFinalWiring.jpeg";
import clipboardSpacers from "@/assets/clipboardSpacers.jpeg";
import clipboardBackSide from "@/assets/clipboardBackSide.jpeg";
import clipboardControl from "@/assets/clipboardControl.jpeg";

// Sample project data - in a real implementation, this would come from a CMS or API
const projectData = {
  'clipboard-dispenser': {
    title: "Accessible Clipboard Dispenser",
    category: "Assistive Devices",
    year: "Jan 2025 – May 2025",
    duration: "4 months",
    team: "Team Lead",
    status: "Completed",
    description: "Designed and prototyped a automatic clipboard dispensor for volunteers with disabilities.",
    challenge: " ",
    solution: "Developed a compact mechanism with guided rails, low-force triggers, and a microcontroller-based actuator sequence for smooth dispense and return cycles.",
    technologies: ["CAD", "3D Printing", "Arduino", "CNC Machining", "Prototyping"],
    features: [
      "Low-force ergonomic trigger",
      "Jam-resistant feed path",
      "Modular maintenance panels",
      "Compact benchtop footprint"
    ],
    results: [
      "Successful deployments in pilot tests",
      "Improved independence for volunteers",
      "Reduced queue time during peak hours"
    ],
    images: [
      dispenserDrawing
    ],
    gallery: [
     
       { src: clipboardSides, caption: "Wooden side panels cut out on my CNC router" },
      { src: clipboardEarlyWiring, caption: "Initial wiring of prototype using WAGOs" },
      { src: clipboardFinalWiring, caption: "Final, soldered wiring of device" },
       { src: clipboardCode, caption: "Code developed and tested in simulator for faster development" },
      { src: clipboardBackSide, caption: "Back of device, with battery, servo, and control box" },
      { src: clipboardControl, caption: "Control box for device, with labeled ports for easier setup" },
       { src: clipboardInterier, caption: "Inside of device, with recessed LEDs on sides" },
       { src: clipboardSpacers, caption: "User swapabble front spacers to allow multiple clipboard sizes" },
       { src: dispenserImage, caption: "Final prototype in operation" },
    ]
  },
  'paper-beam': {
    title: "Composite Paper Beam",
    category: "Materials & Structures",
    year: "April 2024",
    duration: "1 month",
    team: "Team of 4",
    status: "Tested",
    description: "Constructed and tested a paper-based composite beam that supported a 2000 lb+ load using only Elmer's glue and standard printing paper.",
    challenge: "Achieve high load capacity using ultra-low-cost materials while maintaining predictable failure modes and manufacturability.",
    solution: "Optimized laminate stacking, glue line control, and cross-sectional geometry; validated with incremental load testing.",
    technologies: ["Methodology", "Composite Materials", "FEA Assumptions", "Testing"],
    features: [
      "2000 lb+ supported load",
      "Optimized layup schedule",
      "Low-cost manufacturing",
      "Repeatable assembly process"
    ],
    results: [
      "Exceeded target load",
      "Documented failure modes",
      "Presented methodology write-up"
    ],
    images: [
      beamImage
    ],
    gallery: [
      { src: beamTest, caption: "Final beam during load test" }
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
          <p className="text-muted-foreground mb-8">The project you're looking for doesn't exist.</p>
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

            {/* Gallery */}
            {Array.isArray((project as any).gallery) && (project as any).gallery.length > 0 && (
              <Gallery 
                items={(project as any).gallery}
                className="max-w-4xl mx-auto"
              />
            )}

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
                    Interested in this project?
                  </p>
                  <a 
                    href="mailto:engineer@example.com" 
                    className="text-primary hover:underline font-medium"
                  >
                    Let's discuss it
                  </a>
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
