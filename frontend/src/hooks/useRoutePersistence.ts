import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

export const useRoutePersistence = () => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Save current path to localStorage
    localStorage.setItem('lastPath', location.pathname + location.search);
  }, [location]);

  useEffect(() => {
    // On mount, check for saved path
    const lastPath = localStorage.getItem('lastPath');
    if (lastPath && lastPath !== '/' && window.location.pathname === '/') {
      navigate(lastPath);
    }
  }, [navigate]);
};
