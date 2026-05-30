'use client'
import Link from 'next/link'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import RiveHero from '@/app/components/RiveHero'
import { motion, useScroll, useTransform, useInView, AnimatePresence } from 'framer-motion'
import { useRef, useState, useEffect, ReactNode } from 'react'
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'
import { 
  BookOpen, 
  Brain, 
  Target, 
  Upload, 
  Cpu, 
  Gamepad2, 
  Trophy, 
  Star, 
  Zap, 
  Award,
  TrendingUp,
  Users,
  Clock,
  CheckCircle,
  ChevronDown,
  Sparkles,
  Rocket,
  Crown,
  Medal,
  Flame,
  Menu,
  X
} from 'lucide-react'

// Custom Badge Component
const Badge = ({ children, variant = "default", className = "" }: { children: ReactNode, variant?: "default" | "secondary" | "outline" | "destructive", className?: string }) => {
  const variants = {
    default: "bg-blue-600 text-white",
    secondary: "bg-purple-600 text-white",
    outline: "border-2 border-purple-400 text-purple-400 bg-transparent",
    destructive: "bg-red-600 text-white"
  };
  
  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

// Custom Progress Component
const Progress = ({ value, className = "" }: { value: number, className?: string }) => {
  return (
    <div className={`w-full bg-gray-700 rounded-full h-2 ${className}`}>
      <motion.div 
        className="h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
        initial={{ width: 0 }}
        animate={{ width: `${value}%` }}
        transition={{ duration: 1, ease: "easeOut" }}
      />
    </div>
  );
};

// Navbar Component - Removed Dashboard and Pricing
const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
              className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center"
            >
              <Sparkles className="w-5 h-5 text-white" />
            </motion.div>
            <span className="text-xl font-bold text-white">Tayyari</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="#features" className="text-gray-300 hover:text-white transition-colors">
              Features
            </Link>
            <Link href="#how-it-works" className="text-gray-300 hover:text-white transition-colors">
              How it Works
            </Link>
            
            {/* Clerk Authentication - Removed Dashboard buttons */}
            <SignedOut>
              <SignInButton mode="modal">
                <Button variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-800">
                  Sign In
                </Button>
              </SignInButton>
              <Button asChild className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                <Link href="/learn/chat">Get Started</Link>
              </Button>
            </SignedOut>
            
            <SignedIn>
              <Button asChild className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                <Link href="/learn/chat">Continue Learning</Link>
              </Button>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-gray-400 hover:text-white focus:outline-none focus:text-white"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation - Removed Pricing */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden"
            >
              <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-slate-800/50 rounded-lg mt-2">
                <Link href="#features" className="block px-3 py-2 text-gray-300 hover:text-white">
                  Features
                </Link>
                <Link href="#how-it-works" className="block px-3 py-2 text-gray-300 hover:text-white">
                  How it Works
                </Link>
                <div className="flex flex-col space-y-2 px-3 pt-2">
                  <SignedOut>
                    <SignInButton mode="modal">
                      <Button variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-800 w-full">
                        Sign In
                      </Button>
                    </SignInButton>
                    <Button asChild className="bg-gradient-to-r from-blue-600 to-purple-600 w-full">
                      <Link href="/get-started">Get Started</Link>
                    </Button>
                  </SignedOut>
                  
                  <SignedIn>
                    <div className="flex justify-center pt-2">
                      <UserButton afterSignOutUrl="/" />
                    </div>
                  </SignedIn>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
};

// Animated Feature Card Component
const AnimatedFeatureCard = ({ icon: Icon, title, description, color, delay = 0, index, actionButtons }: { icon: any, title: string, description: string, color: string, delay?: number, index: number, actionButtons?: ReactNode }) => {
  const cardRef = useRef(null);
  const isInView = useInView(cardRef, { once: true, margin: "-100px" });
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 50, rotateX: -10 }}
      animate={isInView ? { opacity: 1, y: 0, rotateX: 0 } : { opacity: 0, y: 50, rotateX: -10 }}
      transition={{ duration: 0.6, delay, type: "spring", stiffness: 100 }}
      whileHover={{ 
        scale: 1.02, 
        rotateY: 5,
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)"
      }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="group"
    >
      <Card className="relative h-full bg-gradient-to-br from-slate-800/80 to-slate-900/80 border-slate-700 backdrop-blur-sm overflow-hidden">
        {/* Animated background glow */}
        <motion.div 
          className={`absolute inset-0 bg-gradient-to-br ${color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}
          animate={isHovered ? { scale: 1.1 } : { scale: 1 }}
        />
        
        {/* Floating particles */}
        <AnimatePresence>
          {isHovered && (
            <motion.div className="absolute inset-0 pointer-events-none">
              {[...Array(5)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-2 h-2 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full"
                  initial={{ 
                    opacity: 0, 
                    x: Math.random() * 300, 
                    y: Math.random() * 300,
                    scale: 0 
                  }}
                  animate={{ 
                    opacity: [0, 1, 0], 
                    y: Math.random() * 300 - 50,
                    scale: [0, 1, 0],
                    rotate: 360
                  }}
                  exit={{ opacity: 0 }}
                  transition={{ 
                    duration: 2, 
                    delay: i * 0.2,
                    repeat: Infinity 
                  }}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        <CardHeader className="relative">
          <motion.div 
            className={`w-16 h-16 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-4 mx-auto`}
            animate={isHovered ? { rotate: [0, -10, 10, 0] } : { rotate: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Icon className="w-8 h-8 text-white" />
          </motion.div>
          
          <CardTitle className="text-xl text-center text-white group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-blue-400 group-hover:to-purple-400 group-hover:bg-clip-text transition-all duration-300">
            {title}
          </CardTitle>
        </CardHeader>
        
        <CardContent className="relative">
          <CardDescription className="text-center text-gray-300 leading-relaxed mb-6">
            {description}
          </CardDescription>
        </CardContent>

        <CardFooter className="relative flex flex-col gap-4">
          {/* Action Buttons */}
          <div className="flex gap-2 w-full">
            {actionButtons}
          </div>
          
          {/* Progress Bar */}
          <motion.div 
            className="w-full"
            initial={{ width: 0 }}
            animate={isInView ? { width: "100%" } : { width: 0 }}
            transition={{ duration: 1, delay: delay + 0.5 }}
          >
            <Progress value={85 + index * 5} className="h-2" />
            <div className="flex justify-between mt-2 text-xs text-gray-400">
              <span>Engagement</span>
              <span>{85 + index * 5}%</span>
            </div>
          </motion.div>
        </CardFooter>
      </Card>
    </motion.div>
  );
};

// Achievement Badge Component
const AchievementBadge = ({ icon: Icon, title, earned = false, delay = 0 }: { icon: any, title: string, earned?: boolean, delay?: number }) => {
  return (
    <motion.div
      initial={{ scale: 0, rotate: -180 }}
      animate={{ scale: 1, rotate: 0 }}
      transition={{ 
        delay, 
        type: "spring", 
        stiffness: 200,
        damping: 15 
      }}
      whileHover={{ 
        scale: 1.1, 
        rotate: 5,
        boxShadow: "0 10px 25px rgba(0,0,0,0.3)" 
      }}
      className={`relative p-4 rounded-full ${earned ? 'bg-gradient-to-br from-yellow-400 to-orange-500' : 'bg-slate-700'} transition-all duration-300`}
    >
      <Icon className={`w-6 h-6 ${earned ? 'text-white' : 'text-gray-400'}`} />
      {earned && (
        <motion.div
          className="absolute -top-1 -right-1"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <Sparkles className="w-4 h-4 text-yellow-300" />
        </motion.div>
      )}
      <div className="text-xs text-center mt-2 text-white">{title}</div>
    </motion.div>
  );
};

// Main Component
export default function HomePage() {
  const { scrollYProgress } = useScroll()
  const y = useTransform(scrollYProgress, [0, 1], ['0%', '50%'])
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  
  const featuresRef = useRef(null)
  const processRef = useRef(null)
  
  const featuresInView = useInView(featuresRef, { once: true, margin: "-100px" })
  const processInView = useInView(processRef, { once: true, margin: "-100px" })

  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const features = [
    {
      icon: BookOpen,
      title: "Drop Any Content",
      description: "Transform lectures, research papers, and notes into interactive learning experiences with our AI-powered platform.",
      color: "from-blue-500 to-cyan-500",
      actionButtons: (
        <div className="flex gap-2 w-full">
          <Button size="sm" className="flex-1 bg-blue-600 hover:bg-blue-700">
            Try Now
          </Button>
          <Button size="sm" variant="outline" className="flex-1 border-gray-600 text-black hover:bg-gray-700">
            Learn More
          </Button>
        </div>
      )
    },
    {
      icon: Brain,
      title: "Learn Your Way", 
      description: "AI adapts to your learning style, creating personalized paths that match how your brain processes information best.",
      color: "from-purple-500 to-pink-500",
      actionButtons: (
        <div className="flex gap-2 w-full">
          <Button size="sm" className="flex-1 bg-blue-600 hover:bg-blue-700">
            Explore
          </Button>
          <Button size="sm" variant="outline" className="flex-1 border-gray-600 text-black hover:bg-gray-700">
            Details
          </Button>
        </div>
      )
    },
    {
      icon: Target,
      title: "Make It Stick",
      description: "Reinforce learning with AI-generated quizzes, flashcards, and visual maps designed for long-term retention.",
      color: "from-green-500 to-teal-500",
      actionButtons: (
        <div className="flex gap-2 w-full">
          <Button size="sm" className="flex-1 bg-green-600 hover:bg-green-700">
            Start Quiz
          </Button>
          <Button size="sm" variant="outline" className="flex-1 border-gray-600 text-black hover:bg-gray-700">
            View More
          </Button>
        </div>
      )
    }
  ]

  const processSteps = [
    {
      icon: Upload,
      title: "Upload Your Content",
      description: "Simply drag and drop your learning materials—PDFs, slides, notes, or videos. Our AI instantly processes and understands your content structure.",
      color: "from-blue-500 to-purple-500"
    },
    {
      icon: Cpu,
      title: "AI Processing", 
      description: "Advanced AI algorithms analyze your content, extract key concepts, and create personalized learning paths tailored to your cognitive style.",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: Gamepad2,
      title: "Interactive Learning",
      description: "Engage with dynamic quizzes, interactive summaries, and adaptive content that evolves based on your progress and understanding.",
      color: "from-pink-500 to-red-500"
    }
  ]

  const achievements = [
    { icon: Medal, title: "First Steps", earned: true },
    { icon: Flame, title: "Hot Streak", earned: true },
    { icon: Trophy, title: "Quiz Master", earned: true },
    { icon: Star, title: "Knowledge Seeker", earned: false },
    { icon: Crown, title: "Learning Legend", earned: false },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Navbar */}
      <Navbar />

      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-gradient-to-r from-blue-400/10 to-purple-400/10 rounded-full"
            animate={{
              x: [Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1920), Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1920)],
              y: [Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1080), Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1080)],
              scale: [0, 1, 0],
              opacity: [0, 0.4, 0]
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              delay: Math.random() * 5
            }}
          />
        ))}
      </div>

      {/* Mouse follower effect */}
      <motion.div
        className="fixed w-96 h-96 rounded-full bg-gradient-to-r from-blue-500/3 to-purple-500/3 pointer-events-none z-0 blur-3xl"
        animate={{
          x: mousePosition.x - 192,
          y: mousePosition.y - 192,
        }}
        transition={{ type: "spring", stiffness: 50, damping: 15 }}
      />

      {/* Hero Section - Fully Responsive */}
      <section className="relative w-full min-h-screen flex items-center justify-center overflow-hidden">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="w-full h-full min-h-screen flex items-center justify-center"
          style={{ y, opacity }}
        >
          {/* Responsive RiveHero Container */}
          <div className="w-full h-full min-h-screen max-w-none mx-auto relative">
            {/* Overlay container to ensure proper sizing */}
            <div className="absolute inset-0 w-full h-full">
              <RiveHero />
            </div>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <motion.section 
        ref={featuresRef}
        className="relative px-4 py-16 md:py-20"
        initial={{ opacity: 0 }}
        animate={featuresInView ? { opacity: 1 } : { opacity: 0 }}
        transition={{ duration: 0.8 }}
        id="features"
      >
        <div className="max-w-7xl mx-auto">
          <motion.div 
            className="text-center mb-12 md:mb-16"
            initial={{ opacity: 0, y: 30 }}
            animate={featuresInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-2xl md:text-4xl lg:text-5xl font-bold mb-4 md:mb-6 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Choose Your Learning Adventure
            </h2>
            <p className="text-lg md:text-xl text-gray-300 max-w-3xl mx-auto">
              Three powerful paths to transform how you learn, retain, and master any subject
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
            {features.map((feature, index) => (
              <AnimatedFeatureCard
                key={feature.title}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                color={feature.color}
                delay={index * 0.2}
                index={index}
                actionButtons={feature.actionButtons}
              />
            ))}
          </div>
        </div>
      </motion.section>

      {/* Process Section */}
      <motion.section 
        ref={processRef}
        className="relative px-4 py-16 md:py-20"
        initial={{ opacity: 0 }}
        animate={processInView ? { opacity: 1 } : { opacity: 0 }}
        transition={{ duration: 0.8 }}
        id="how-it-works"
      >
        <div className="max-w-7xl mx-auto">
          <motion.div 
            className="text-center mb-12 md:mb-16"
            initial={{ opacity: 0, y: 30 }}
            animate={processInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-2xl md:text-4xl lg:text-5xl font-bold mb-4 md:mb-6 text-white">
              Your Learning Journey
            </h2>
            <p className="text-lg md:text-xl text-gray-300 max-w-3xl mx-auto">
              From upload to mastery in three gamified steps
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
            {processSteps.map((step, index) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, x: -50 }}
                animate={processInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -50 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                whileHover={{ scale: 1.03 }}
                className="relative"
              >
                <Card className="h-full bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300">
                  <CardHeader className="text-center">
                    <motion.div 
                      className={`w-16 md:w-20 h-16 md:h-20 rounded-full bg-gradient-to-br ${step.color} flex items-center justify-center mx-auto mb-4 relative`}
                      whileHover={{ rotate: 360 }}
                      transition={{ duration: 0.8 }}
                    >
                      <step.icon className="w-8 md:w-10 h-8 md:h-10 text-white" />
                      
                      {/* Step number badge */}
                      <motion.div 
                        className="absolute -top-2 -right-2 w-6 md:w-8 h-6 md:h-8 bg-yellow-400 text-black rounded-full flex items-center justify-center font-bold text-xs md:text-sm"
                        initial={{ scale: 0 }}
                        animate={processInView ? { scale: 1 } : { scale: 0 }}
                        transition={{ delay: index * 0.2 + 0.5 }}
                      >
                        {index + 1}
                      </motion.div>
                    </motion.div>
                    
                    <CardTitle className="text-lg md:text-xl text-white">{step.title}</CardTitle>
                  </CardHeader>
                  
                  <CardContent>
                    <CardDescription className="text-gray-300 leading-relaxed text-sm md:text-base">
                      {step.description}
                    </CardDescription>
                  </CardContent>
                </Card>

                {/* Connecting line - Hidden on mobile */}
                {index < processSteps.length - 1 && (
                  <motion.div 
                    className="hidden md:block absolute top-1/2 left-full w-8 h-0.5 bg-gradient-to-r from-purple-500 to-transparent z-10"
                    initial={{ scaleX: 0 }}
                    animate={processInView ? { scaleX: 1 } : { scaleX: 0 }}
                    transition={{ delay: index * 0.2 + 0.8, duration: 0.6 }}
                  />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* CTA Section - Removed Dashboard references */}
      <motion.section 
        className="relative px-4 py-16 md:py-20"
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true }}
      >
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            className="bg-gradient-to-r from-slate-800/50 via-slate-700/50 to-slate-800/50 rounded-2xl p-8 md:p-12 backdrop-blur-sm border border-slate-600/30"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.3 }}
          >
            <h2 className="text-2xl md:text-4xl lg:text-5xl font-bold mb-4 md:mb-6 text-white">
              Ready to Level Up?
            </h2>
            <p className="text-lg md:text-xl text-gray-300 mb-6 md:mb-8 max-w-2xl mx-auto">
              Join thousands of learners earning XP, unlocking achievements, and mastering new skills every day.
            </p>
            
            <motion.div 
              className="flex flex-col sm:flex-row gap-4 justify-center"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <SignedOut>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button 
                    asChild 
                    size="lg" 
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0 px-6 md:px-8 py-4 md:py-6 text-base md:text-lg font-semibold w-full sm:w-auto"
                  >
                    <Link href="/learn/chat" className="flex items-center gap-2 justify-center">
                      <Zap className="w-5 h-5" />
                      Begin Your Journey
                    </Link>
                  </Button>
                </motion.div>
              </SignedOut>
              
              <SignedIn>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button 
                    asChild 
                    size="lg" 
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0 px-6 md:px-8 py-4 md:py-6 text-base md:text-lg font-semibold w-full sm:w-auto"
                  >
                    <Link href="/learn/chat" className="flex items-center gap-2 justify-center">
                      <Rocket className="w-5 h-5" />
                      Continue Learning
                    </Link>
                  </Button>
                </motion.div>
              </SignedIn>
              
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button 
                  variant="outline" 
                  size="lg" 
                  className="border-2 border-purple-400 text-purple-400 hover:bg-purple-400 hover:text-white px-6 md:px-8 py-4 md:py-6 text-base md:text-lg font-semibold w-full sm:w-auto"
                >
                  <Users className="w-5 h-5 mr-2" />
                  Join Community
                </Button>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </motion.section>
    </div>
  )
}