import Header from "@/components/Header";
import Hero from "@/components/Hero";
import ProjectsShowcase from "@/components/ProjectsShowcase";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <Hero />
        <ProjectsShowcase />
        
        {/* About Section */}
        <section id="about" className="py-20 bg-muted/20">
          <div className="container mx-auto px-6">
            <div className="max-w-4xl mx-auto">
              <div className="grid md:grid-cols-2 gap-12 items-center">
                <div>
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-background/50 border border-border mb-4">
                    <span className="w-2 h-2 bg-primary rounded-full"></span>
                    <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
                      About Me
                    </span>
                  </div>
                  
                  <h2 className="text-3xl font-bold mb-6">
                    Passionate About
                    <span className="block text-primary">Mechanical Innovation</span>
                  </h2>
                  
                  <p className="text-muted-foreground mb-6 leading-relaxed">
                    As a mechanical engineering student, I'm driven by the challenge of solving 
                    complex problems through innovative design and precise engineering. My work 
                    spans from CAD modeling and finite element analysis to hands-on prototyping 
                    and testing.
                  </p>
                  
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-primary rounded-full"></div>
                      <span className="text-sm">SolidWorks & AutoCAD Certified</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-technical-orange rounded-full"></div>
                      <span className="text-sm">Experience with FEA & CFD Analysis</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-accent rounded-full"></div>
                      <span className="text-sm">3D Printing & Rapid Prototyping</span>
                    </div>
                  </div>
                </div>
                
                <div className="relative">
                  <div className="aspect-square bg-gradient-to-br from-primary/10 to-accent/10 rounded-lg flex items-center justify-center border border-border/50">
                    <div className="text-center">
                      <div className="w-24 h-24 mx-auto mb-4 bg-primary/20 rounded-lg flex items-center justify-center">
                        <svg className="w-12 h-12 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                        </svg>
                      </div>
                      <p className="font-mono text-sm text-muted-foreground">Engineering Excellence</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        {/* Contact Section */}
        <section id="contact" className="py-20">
          <div className="container mx-auto px-6">
            <div className="max-w-2xl mx-auto text-center">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-muted/50 border border-border mb-4">
                <span className="w-2 h-2 bg-primary rounded-full"></span>
                <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
                  Get In Touch
                </span>
              </div>
              
              <h2 className="text-3xl font-bold mb-6">
                Let's Collaborate
              </h2>
              
              <p className="text-muted-foreground mb-8 leading-relaxed">
                Interested in discussing engineering projects, internship opportunities, 
                or potential collaborations? I'd love to hear from you.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a 
                  href="mailto:engineer@example.com" 
                  className="inline-flex items-center justify-center px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                >
                  <svg className="mr-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 7.89a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Email Me
                </a>
                <a 
                  href="https://linkedin.com/in/your-profile" 
                  className="inline-flex items-center justify-center px-6 py-3 border border-border rounded-md hover:bg-muted/50 transition-colors"
                >
                  <svg className="mr-2 w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                  LinkedIn
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      {/* Footer */}
      <footer className="border-t border-border bg-muted/20 py-8">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="font-mono text-sm text-muted-foreground mb-4 md:mb-0">
              © 2024 Mechanical Engineer Portfolio
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span>Built with precision</span>
              <div className="w-1 h-1 bg-primary rounded-full"></div>
              <span>Designed for impact</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
