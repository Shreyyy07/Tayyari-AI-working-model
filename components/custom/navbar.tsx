"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import Link from "next/link";
import { Separator } from "../ui/separator";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton,
} from "@clerk/nextjs";
import { Menu, X, Sparkles, BookOpen, Trophy } from "lucide-react";

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <motion.nav
  className={`fixed top-0 w-full z-[100] transition-all duration-300 ${
    isScrolled
      ? 'bg-gray-900/95 backdrop-blur-lg border-b border-gray-700/50 shadow-lg'
      : 'bg-gray-900/80 backdrop-blur-sm'
  }`}
  initial={{ y: -100 }}
  animate={{ y: 0 }}
  transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo */}
          <motion.div
            className="flex items-center space-x-2 cursor-pointer group"
            onClick={() => window.location.href = '/'}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="relative">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center shadow-lg group-hover:shadow-purple-500/25 transition-all">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div className="absolute -inset-1 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg opacity-30 blur group-hover:opacity-50 transition-opacity"></div>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
              Tayyari.ai
            </span>
          </motion.div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              href="/learn/chat"
              className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors group"
            >
              <BookOpen size={16} className="group-hover:text-purple-400 transition-colors" />
              <span className="font-medium">Learn</span>
            </Link>
            
            <Link
              href="/leaderboard"
              className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors group"
            >
              <Trophy size={16} className="group-hover:text-yellow-400 transition-colors" />
              <span className="font-medium">Leaderboard</span>
            </Link>
          </div>

          {/* Clerk Auth Buttons */}
          <div className="flex items-center space-x-4">
            <SignedIn>
              <div className="flex items-center space-x-3">
                {/* User greeting - hidden on small screens */}
                <div className="hidden sm:block text-sm text-gray-300">
                  Welcome back! 👋
                </div>
                
                {/* Custom styled UserButton */}
                <div className="relative">
                  <div className="absolute -inset-1 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full opacity-30 blur-sm"></div>
                  <div className="relative">
                    <UserButton
                      appearance={{
                        elements: {
                          avatarBox: "w-10 h-10 rounded-full border-2 border-purple-500/50 shadow-lg hover:border-purple-400 transition-colors",
                          userButtonPopoverCard: "bg-gray-800 border border-gray-700 shadow-xl",
                          userButtonPopoverActions: "text-gray-300 hover:text-white",
                          userButtonPopoverActionButton: "hover:bg-gray-700",
                        }
                      }}
                    />
                  </div>
                </div>
              </div>
            </SignedIn>

            <SignedOut>
              <div className="flex items-center space-x-3">
                <SignInButton>
                  <Button 
                    variant="ghost" 
                    className="hidden sm:flex text-gray-300 hover:text-white hover:bg-gray-800/50"
                  >
                    Sign in
                  </Button>
                </SignInButton>
                
                <SignUpButton>
                  <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg hover:shadow-purple-500/25 transition-all hover:scale-105">
                    Sign up
                  </Button>
                </SignUpButton>
              </div>
            </SignedOut>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden text-gray-300 hover:text-white transition-colors p-2 hover:bg-gray-800/50 rounded-lg"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <motion.div
            className="md:hidden border-t border-gray-700/50 bg-gray-900/95 backdrop-blur-lg"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="px-4 py-4 space-y-4">
              {/* Mobile Navigation Links */}
              <div className="space-y-2">
                <Link
                  href="/learn/chat"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="flex items-center space-x-3 text-gray-300 hover:text-white transition-colors p-3 rounded-lg hover:bg-gray-800/50"
                >
                  <BookOpen size={18} />
                  <span className="font-medium">Learn</span>
                </Link>
                
                <Link
                  href="/leaderboard"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="flex items-center space-x-3 text-gray-300 hover:text-white transition-colors p-3 rounded-lg hover:bg-gray-800/50"
                >
                  <Trophy size={18} />
                  <span className="font-medium">Leaderboard</span>
                </Link>
              </div>

              {/* Mobile Auth Buttons */}
              <SignedOut>
                <Separator className="bg-gray-700/50" />
                <div className="space-y-2">
                  <SignInButton>
                    <Button 
                      variant="outline" 
                      className="w-full border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white"
                    >
                      Sign in
                    </Button>
                  </SignInButton>
                  
                  <SignUpButton>
                    <Button className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white">
                      Sign up
                    </Button>
                  </SignUpButton>
                </div>
              </SignedOut>
            </div>
          </motion.div>
        )}
      </div>
    </motion.nav>
  );
}
