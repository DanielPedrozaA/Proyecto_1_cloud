import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Login from './components/Login/Login.js';
import Signup from './components/Signup/Signup.js';
import { Routes, Route } from 'react-router-dom';


const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
    </Routes>
  );
};

export default App;