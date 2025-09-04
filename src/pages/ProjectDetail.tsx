
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


import beamGraph from "@/assets/graph.png";

import beamGraph from "@/assets/graph.png";
import controllerHero from "@/assets/controllerHero.png";
import controllerImage from "@/assets/controllerImage.png";
import controllerGif from "@/assets/controllerGif.gif";
import controllerWC from "@/assets/controllerWC.png";

import hangHook from "@/assets/hangHook.png";
import hangHookAssembly from "@/assets/hangClipAssembly.gif";
import hangHookOpen from "@/assets/hangClipOpen.jpeg";
import hangHookFold from "@/assets/hangClipFold.jpeg";
import hangHookColors from "@/assets/HangClipColors.jpeg";
import hangHookFEA from "@/assets/hangClipFEA.png";
// Sample project data - in a real implementation, this would come from a CMS or API
const projectData = {
  'clipboard-dispenser': {
    title: "Accessible Clipboard Dispenser",
    category: "",
    year: "Jan 2025 – May 2025",
    duration: "4 months",
    team: "Team Lead",
    status: "Completed",
    description: "Designed and prototyped an automatic clipboard dispensor for volunteers with disabilities.",
    challenge: "A charity had an operation where individuals with severe disabilites could create items for donation. This was Accomplished via dedicated stations for each step. My team and I observed a engagement and efficiency issue at the first station, where the user was instructed to obtain a clipboard.",
    solution: "Designed a device that reliably dispenses clipboards for the user via a red button. This final prototype is based off of 2 previous prototypes and constant communication with the stakeholders.",
    technologies: ["CAD", "3D Printing", "Arduino", "CNC Machining", "Prototyping"],
    features: [
      "Extremely simple operation",
      "Jam-resistant mechanism",
      "All day battery life",
      "Compact and portable footprint",
      "Easy setup, and easy charging with USB-C",
      "Stakeholder requested features inlcuding: LED lights, window and ramp with rollers",
      "Long wire on button ensures that a user can press it. the button can be moved within arms reach, placed on the floor and operated by foot, or be held by an assistent for users in wheelchairs"
    ],
    results: [
      "50% increase in engagment",
      "Reduced station time to 15s",
      "Allows users to be more independent"
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
    category: "Materials",
    year: "April 2024",
    duration: "1 month",
    team: "Solo",
    status: "Completed",
    description: "Constructed and tested a paper and glue composite beam that supported a 2000 lb+ load, breaking the university record",
    challenge: "The challenge was to construct a paper beam that could support atlaest 200lbs. The beam could only be made with Elmer's glue, and standard 8.5 x 11 printer paper. Additionally, I was aiming to break the 8 year university record of ~1800lbs.",
    solution: "Maximized final composite strength by developing a precise fabrication methodology using custom jigs for uniform cutting, glue application, and pressing",
    technologies: ["Methodology", "Composite Materials", "Testing"],
    features: [
      "2000 lb+ supported load",
      "Repeatable assembly process"
    ],
    results: [
      "Exceeded target load",
      "Set a new record"
    ],
    images: [
      beamImage
    ],
    gallery: [
      { src: beamTest, caption: "Final beam during load test" },
      { src: beamGraph, caption: "Load cell graph. Paper beam compared to wood beams of similar size.\n (note: the test limits were set to 2000lbs)" }
    ]
  },
    'controller': {
    title: "Controller Accessability Addon",
    category: "Accessability",
    year: "December 2021",
    duration: "1 month",
    team: "Solo",
    status: "Completed",
    description: "Designed a addon for the Nintendo Switch Pro Controller to allow for easier use of triggers and bumpers for people with disabilites.",
    challenge: "Designed for a design competition. The goal was to design a 3D printable addon that would help increase accessability in gaming. I noticed that there werent many addons for the controller I had on hand, the Nintendo Switch Pro Controller, so I focused on that",
    solution: "I designed a print in place snap on addon that allows the bumpers and triggers to be used from the front of the controller",
    technologies: ["CAD Design", "3D Printing"],
    features: [
      "Open Source",
      "Threaded hole on the back to allow greater adaptability",
      "Print in place",
      "Easy installation and removal",
      "Keeps the USB-C port accessable"
    ],
    results: [
      "Featuered on the list of controller modifications maintained by The Controller Project",
    ],
    images: [
      controllerHero
    ],
    gallery: [
      { src: controllerImage, caption: "Addon attached to controller" },
      { src: controllerGif, caption: "Device in use" },
      { src: controllerWC, caption: "CAD design with 3D scan of controller" }
    ],
    links: [
      { url: "https://www.printables.com/model/103432-nintendo-switch-pro-controller-print-in-place-snap", text: "View On Printables" }
    ]
  },
      'hangClip': {
    title: "HangClip - 3D printable folding bag hanger",
    category: "",
    year: "September 2024",
    duration: "1 month",
    team: "Solo",
    status: "Completed",
    description: "A folding bag hanger to hang a bag off the edge of a table",
    challenge: "Designed for a design competition. The goal was to design a 3D printable item with the that involved storage",
    solution: "I designed and tested a strong 3D printable hook that can hold 10lbs - 25lbs, for the fully 3D printed and hardware version respectively.\n  Tested design with FEA analysis and weight testing (tested until faliure)",
    technologies: ["CAD Design", "3D Printing", "FEA"],
    features: [
      "Folds around bag handle so its always accessable",
      "Dimple on hook ensures the clip locks when folded, preventing loss",
      "can be fully 3D printed, or with a M3 bolt & Locknut",
      "Easy to use",
      "Works on tables, bathroom stalls, railing, and more"
    ],
    results: [
      "500+ Downloads",
      "250+ 3D Prints"
    ],
    images: [
      hangHook
    ],
    gallery: [
        { src: hangHookOpen, caption: "HangClip in use" },
      { src: hangHookFold, caption: "HangClip folded on backpack" },
      { src: hangHookColors, caption: "Final Design" },
      { src: hangHookFEA, caption: "FEA analysis on recommended load" },
      { src: hangHookAssembly, caption: "video demonstrating assemely process" }
    ],
    links: [
      { url: "https://makerworld.com/en/models/648762-hangclip-a-simple-folding-bag-hanger", text: "View On Makerworld" },
      { url: "https://www.printables.com/model/1010952-hangclip-a-simple-folding-bag-hanger", text: "View On Printables" }
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
          <p className="text-muted-foreground mb-8">The project you're looking for doesn't exist, or the page has not been completed yet. Check back soon!.</p>
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
                                {/* Links */}
                {Array.isArray((project as any).links) && (project as any).links.length > 0 && (
                  <div className="bg-muted/20 p-6 rounded-lg border border-border/50">
                    <h3 className="font-bold mb-4">Links</h3>
                    <div className="space-y-3">
                      {(project as any).links.map((link: { url: string; text: string }, index: number) => (
                        <a
                          key={index}
                          href={link.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block text-sm text-muted-foreground hover:text-foreground transition-colors hover:underline"
                        >
                          {link.text}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
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
