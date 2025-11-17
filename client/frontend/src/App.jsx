import './App.css'
import { useEffect, useState } from 'react'
import { Routes, Route } from "react-router-dom"
import { useSelector, useDispatch } from 'react-redux';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.js';
import Devices from './Devices'
import HomePage from './HomePage'
import { fetchInterfaces } from './redux/interfacesSlice';

function App() {
  const [remoteIp, setRemoteIp] = useState('');
  const { interfaces, status, error } = useSelector((state) => state.interfaces);
  const dispatch = useDispatch();

  useEffect (() => {
    if (status === 'idle') {
      dispatch(fetchInterfaces());
    }
  }, [status]);

  if (status === 'loading') return <p>Loading...</p>;
  if (status === 'failed') return (
    <div style={{color: 'red',textAlign: 'center', whiteSpace: 'pre-wrap'}}>
      <h1>{error}</h1>
      <h3>Use the link below to pull the local backserver image.</h3>
      <h3>Follow the instructions in the link.</h3>
        <a href="https://hub.docker.com/r/sagivlevi1509/iot-anomalies-detector" target="_blank" rel="noopener noreferrer">Pull Local Backserver Image</a>
    </div>
    )
  return (
    <>
      {interfaces.length > 0 ? (
        <div>
          <Routes>
            <Route path='/' element={<HomePage />} />
            <Route path='/devices/:router_mac' element={<Devices />} />
          </Routes>
        </div>
        ) : (
            <p>No interfaces found.</p>
        )}
    </>
)}

export default App