import React from 'react';
import ContainerSimulator from './components/ContainerSimulator';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-docker-blue text-white shadow-md">
        <div className="container mx-auto py-4 px-6">
          <h1 className="text-3xl font-bold">Docker Kitchen</h1>
          <p className="text-lg">³óÆÊ¡·ßåìü¿ü</p>
        </div>
      </header>
      <main className="container mx-auto py-8 px-4">
        <ContainerSimulator />
      </main>
    </div>
  );
}

export default App;