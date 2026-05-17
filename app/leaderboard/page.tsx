'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useUser } from '@clerk/nextjs';
import toast, { Toaster } from 'react-hot-toast';
import { 
  Trophy, 
  Crown, 
  Medal, 
  Star, 
  Flame, 
  Target, 
  Calendar,
  Users,
  TrendingUp,
  Award,
  Zap,
  BookOpen,
  Clock,
  ChevronUp,
  ChevronDown
} from 'lucide-react';

interface LeaderboardUser {
  id: string;
  name: string;
  avatar?: string;
  points: number;
  level: number;
  streak: number;
  totalQuizzes: number;
  averageScore: number;
  joinedDate: string;
  badges: string[];
  weeklyPoints: number;
  monthlyPoints: number;
  rank: number;
  previousRank: number;
  isCurrentUser?: boolean;
}

interface LeaderboardStats {
  totalUsers: number;
  averagePoints: number;
  topStreakUser: string;
  mostActiveDay: string;
}

export default function EnhancedLeaderboard() {
  const { user } = useUser();
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardUser[]>([]);
  const [currentUserRank, setCurrentUserRank] = useState<LeaderboardUser | null>(null);
  const [stats, setStats] = useState<LeaderboardStats | null>({
  totalUsers: 0,
  averagePoints: 0,
  topStreakUser: 'N/A',
  mostActiveDay: 'Loading...'
});
  const [timeFilter, setTimeFilter] = useState<'weekly' | 'monthly' | 'alltime'>('alltime');
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<'points' | 'quizzes' | 'streak'>('points');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isLive, setIsLive] = useState(false);

  // Fetch leaderboard data from API
  useEffect(() => {
    fetchLeaderboardData();
    const interval = setInterval(fetchLeaderboardData, 15000); // Update every 15 seconds
    return () => clearInterval(interval);
  }, [timeFilter, selectedCategory]);


const fetchLeaderboardData = async () => {
  try {
    setIsLive(false);
    const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') || 'http://localhost:5000';
    const response = await fetch(`${BACKEND_URL}/api/leaderboard?timeFilter=${timeFilter}&category=${selectedCategory}&userId=${user?.id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.status === 'success') {
      setLeaderboardData(data.leaderboard || []);
      setCurrentUserRank(data.currentUserRank);
      
      setStats({
        totalUsers: data.stats?.totalUsers || data.stats?.total_users || 0,
        averagePoints: data.stats?.averagePoints || data.stats?.average_points || 0,
        topStreakUser: data.stats?.topStreakUser || data.stats?.top_streak_user || 'N/A',
        mostActiveDay: data.stats?.mostActiveDay || data.stats?.most_active_day || 'Monday'
      });
      
      setLastUpdated(new Date());
      setIsLive(true);
      console.log('✅ Leaderboard data loaded successfully');
    } else {
      throw new Error(data.message || 'Failed to load leaderboard');
    }
  } catch (error) {
    console.error('❌ Error fetching leaderboard:', error);
    
    setLeaderboardData([]);
    setCurrentUserRank(null);
    setStats({
      totalUsers: 0,
      averagePoints: 0,
      topStreakUser: 'N/A',
      mostActiveDay: 'N/A'
    });
    setIsLive(false);
  } finally {
    setLoading(false);
  }
};

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1: return <Crown className="text-yellow-400" size={24} />;
      case 2: return <Medal className="text-gray-300" size={24} />;
      case 3: return <Medal className="text-amber-600" size={24} />;
      default: return <Trophy className="text-purple-400" size={20} />;
    }
  };

  const getRankChange = (current: number, previous: number) => {
    if (current < previous) return { icon: <ChevronUp className="text-green-400" size={16} />, color: 'text-green-400' };
    if (current > previous) return { icon: <ChevronDown className="text-red-400" size={16} />, color: 'text-red-400' };
    return { icon: null, color: 'text-gray-400' };
  };

  const getScoreForCategory = (userData: LeaderboardUser) => {
    switch (selectedCategory) {
      case 'points': return userData.points;
      case 'quizzes': return userData.totalQuizzes;
      case 'streak': return userData.streak;
      default: return userData.points;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white pt-20">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        
        {/* Header Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center mb-4">
            <Trophy className="text-yellow-400 mr-3" size={40} />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
              Learning Champions
            </h1>
          </div>
          <p className="text-gray-400 text-lg">
            🚀 Compete, Learn, and Level Up with Fellow Learners!
          </p>
          {/* Live indicator */}
          <div className="flex items-center justify-center gap-2 mt-3">
            <span className={`inline-block w-2 h-2 rounded-full ${isLive ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
            <span className="text-sm text-gray-400">
              {isLive ? (
                <>Live · refreshes every 15s{lastUpdated && <> · Updated {lastUpdated.toLocaleTimeString()}</>}</>
              ) : 'Connecting...'}
            </span>
          </div>
        </motion.div>

        {/* Stats Cards */}
{stats && (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
  >
    <div className="bg-gradient-to-br from-purple-600/20 to-blue-600/20 backdrop-blur-sm rounded-xl p-4 border border-purple-500/30">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-purple-300 text-sm">Total Learners</p>
          <p className="text-2xl font-bold text-white">
            {(stats?.totalUsers || 0).toLocaleString()}
          </p>
        </div>
        <Users className="text-purple-400" size={32} />
      </div>
    </div>

    <div className="bg-gradient-to-br from-green-600/20 to-emerald-600/20 backdrop-blur-sm rounded-xl p-4 border border-green-500/30">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-green-300 text-sm">Avg Points</p>
          <p className="text-2xl font-bold text-white">
            {Math.round(stats?.averagePoints || 0).toLocaleString()}
          </p>
        </div>
        <TrendingUp className="text-green-400" size={32} />
      </div>
    </div>

    <div className="bg-gradient-to-br from-orange-600/20 to-red-600/20 backdrop-blur-sm rounded-xl p-4 border border-orange-500/30">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-orange-300 text-sm">Streak King</p>
          <p className="text-lg font-bold text-white truncate">
            {stats?.topStreakUser || 'N/A'}
          </p>
        </div>
        <Flame className="text-orange-400" size={32} />
      </div>
    </div>

    <div className="bg-gradient-to-br from-blue-600/20 to-indigo-600/20 backdrop-blur-sm rounded-xl p-4 border border-blue-500/30">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-blue-300 text-sm">Peak Day</p>
          <p className="text-lg font-bold text-white">
            {stats?.mostActiveDay || 'Monday'}
          </p>
        </div>
        <Calendar className="text-blue-400" size={32} />
      </div>
    </div>
  </motion.div>
)}

        {/* Filter Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-wrap gap-4 mb-8 bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-gray-700/50"
        >
          {/* Time Filter */}
          <div className="flex space-x-2">
            {[
              { key: 'alltime', label: 'All Time', icon: <Clock size={16} /> },
              { key: 'monthly', label: 'This Month', icon: <Calendar size={16} /> },
              { key: 'weekly', label: 'This Week', icon: <Target size={16} /> }
            ].map(({ key, label, icon }) => (
              <button
                key={key}
                onClick={() => setTimeFilter(key as any)}
                className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center space-x-2 ${
                  timeFilter === key
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
                }`}
              >
                {icon}
                <span>{label}</span>
              </button>
            ))}
          </div>

          {/* Category Filter */}
          <div className="flex space-x-2">
            {[
              { key: 'points', label: 'Points', icon: <Star size={16} /> },
              { key: 'quizzes', label: 'Quizzes', icon: <BookOpen size={16} /> },
              { key: 'streak', label: 'Streak', icon: <Flame size={16} /> }
            ].map(({ key, label, icon }) => (
              <button
                key={key}
                onClick={() => setSelectedCategory(key as any)}
                className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center space-x-2 ${
                  selectedCategory === key
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
                }`}
              >
                {icon}
                <span>{label}</span>
              </button>
            ))}
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Current User Rank Card */}
          {currentUserRank && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="lg:col-span-1"
            >
              <div className="bg-gradient-to-br from-purple-600/20 to-blue-600/20 backdrop-blur-sm rounded-xl p-6 border border-purple-500/30 sticky top-24">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <Award className="mr-2 text-purple-400" size={20} />
                  Your Rank
                </h3>
                
                <div className="text-center mb-4">
                  <div className="text-6xl font-bold text-purple-400 mb-2">
                    #{currentUserRank.rank}
                  </div>
                  <div className="flex items-center justify-center space-x-2">
                    {getRankChange(currentUserRank.rank, currentUserRank.previousRank).icon}
                    <span className={getRankChange(currentUserRank.rank, currentUserRank.previousRank).color}>
                      {currentUserRank.previousRank !== currentUserRank.rank 
                        ? `${Math.abs(currentUserRank.rank - currentUserRank.previousRank)} places`
                        : 'No change'
                      }
                    </span>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Points</span>
                    <span className="text-yellow-400 font-semibold">{currentUserRank.points.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Level</span>
                    <span className="text-blue-400 font-semibold">Level {currentUserRank.level}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Streak</span>
                    <span className="text-orange-400 font-semibold flex items-center">
                      <Flame size={16} className="mr-1" />
                      {currentUserRank.streak}
                    </span>
                  </div>
                </div>

                {/* User Badges */}
                {currentUserRank.badges.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Recent Badges</h4>
                    <div className="flex flex-wrap gap-1">
                      {currentUserRank.badges.slice(0, 3).map((badge, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 text-yellow-300 text-xs rounded-full border border-yellow-500/30"
                        >
                          {badge}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Leaderboard List */}
          <div className="lg:col-span-3">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700/50 overflow-hidden">
              {/* Header */}
              <div className="bg-gradient-to-r from-gray-800 to-gray-700 px-6 py-4 border-b border-gray-600/50">
                <h3 className="text-xl font-semibold text-white flex items-center">
                  <Trophy className="mr-2 text-yellow-400" size={24} />
                  Top Performers
                </h3>
              </div>

              {/* Loading State */}
              {loading ? (
                <div className="p-8 text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
                  <p className="text-gray-400">Loading champions...</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-700/50">
                  <AnimatePresence>
                    {leaderboardData.map((userData, index) => (
                      <motion.div
                        key={userData.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ delay: index * 0.05 }}
                        className={`p-6 hover:bg-gray-700/30 transition-all duration-300 ${
                          userData.isCurrentUser 
                            ? 'bg-gradient-to-r from-purple-600/10 to-blue-600/10 border-l-4 border-purple-500' 
                            : ''
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          {/* Left Side - Rank & User Info */}
                          <div className="flex items-center space-x-4">
                            {/* Rank */}
                            <div className="flex items-center space-x-2 min-w-[80px]">
                              {getRankIcon(userData.rank)}
                              <div className="text-center">
                                <div className="text-2xl font-bold text-white">#{userData.rank}</div>
                                {userData.previousRank !== userData.rank && (
                                  <div className="flex items-center justify-center">
                                    {getRankChange(userData.rank, userData.previousRank).icon}
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* User Info */}
                            <div className="flex items-center space-x-3">
                              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                                {userData.name.charAt(0).toUpperCase()}
                              </div>
                              <div>
                                <h4 className="text-lg font-semibold text-white flex items-center">
                                  {userData.name}
                                  {userData.isCurrentUser && (
                                    <span className="ml-2 px-2 py-1 bg-purple-600 text-white text-xs rounded-full">
                                      You
                                    </span>
                                  )}
                                </h4>
                                <div className="flex items-center space-x-3 text-sm text-gray-400">
                                  <span>Level {userData.level}</span>
                                  <span className="flex items-center">
                                    <Flame className="mr-1" size={12} />
                                    {userData.streak} day streak
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Right Side - Stats */}
                          <div className="text-right">
                            <div className="text-2xl font-bold text-yellow-400 mb-1">
                              {getScoreForCategory(userData).toLocaleString()}
                              <span className="text-sm text-gray-400 ml-1">
                                {selectedCategory === 'points' ? 'pts' : selectedCategory === 'quizzes' ? 'quizzes' : 'days'}
                              </span>
                            </div>
                            <div className="text-sm text-gray-400">
                              Avg Score: {userData.averageScore}%
                            </div>
                            
                            {/* Badges */}
                            {userData.badges.length > 0 && (
                              <div className="flex justify-end mt-2 space-x-1">
                                {userData.badges.slice(0, 2).map((badge, badgeIndex) => (
                                  <span
                                    key={badgeIndex}
                                    className="px-2 py-1 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 text-yellow-300 text-xs rounded-full border border-yellow-500/30"
                                  >
                                    {badge}
                                  </span>
                                ))}
                                {userData.badges.length > 2 && (
                                  <span className="px-2 py-1 bg-gray-600/50 text-gray-300 text-xs rounded-full">
                                    +{userData.badges.length - 2}
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Progress Bar for Top 3 */}
                        {index < 3 && (
                          <div className="mt-4">
                            <div className="w-full bg-gray-700 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full transition-all duration-1000 ${
                                  index === 0 ? 'bg-gradient-to-r from-yellow-400 to-orange-500' :
                                  index === 1 ? 'bg-gradient-to-r from-gray-300 to-gray-400' :
                                  'bg-gradient-to-r from-amber-600 to-amber-700'
                                }`}
                                style={{
                                  width: `${Math.min(100, (getScoreForCategory(userData) / Math.max(...leaderboardData.map(u => getScoreForCategory(u)))) * 100)}%`
                                }}
                              ></div>
                            </div>
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Achievement Showcase */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-12 bg-gradient-to-r from-purple-600/10 to-blue-600/10 backdrop-blur-sm rounded-xl p-6 border border-purple-500/30"
        >
          <h3 className="text-2xl font-bold text-white mb-4 flex items-center">
            <Zap className="mr-2 text-yellow-400" size={24} />
            Recent Achievements
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-800/50 rounded-lg p-4 border border-yellow-500/30">
              <div className="flex items-center space-x-3">
                <Crown className="text-yellow-400" size={32} />
                <div>
                  <h4 className="text-white font-semibold">Quiz Master</h4>
                  <p className="text-gray-400 text-sm">Perfect score on 5 quizzes</p>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800/50 rounded-lg p-4 border border-orange-500/30">
              <div className="flex items-center space-x-3">
                <Flame className="text-orange-400" size={32} />
                <div>
                  <h4 className="text-white font-semibold">Streak Legend</h4>
                  <p className="text-gray-400 text-sm">30-day learning streak</p>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800/50 rounded-lg p-4 border border-blue-500/30">
              <div className="flex items-center space-x-3">
                <BookOpen className="text-blue-400" size={32} />
                <div>
                  <h4 className="text-white font-semibold">Knowledge Seeker</h4>
                  <p className="text-gray-400 text-sm">Completed 100 lessons</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}