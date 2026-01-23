import { useState, useEffect } from "react";


function App(){
  const [recuerdos, setRecuerdos] = useState([]);
  const [archivo, setArchivo] = useState(null);

  const [nuevoRecuerdo, setNuevoRecuerdo] = useState({
    titulo: '',
    desc: '',
    palabra: ''
  })

  const traerDatos = async () => {
    const respuesta = await fetch('https://api-recuerdos-nullvoice.onrender.com/recuerdos')    
    const datos = await respuesta.json()
    setRecuerdos(datos)
  }

  useEffect(() => {
    traerDatos()
  }, [])


  const borrarRecuerdo = async (id) => {
    if (!window.confirm("¿Estás seguro de que quieres borrar este recuerdo?")) return;
    try {
        // CAMBIO: Borra en tu PC
        const respuesta = await fetch(`https://api-recuerdos-nullvoice.onrender.com/${id}`, {          
            method: 'DELETE',
        });
        if (respuesta.ok) traerDatos(); 
    } catch (error) {
        console.error("Error en la conexión:", error);
    }
  };

  const guardarConFoto = async (e) => {
    e.preventDefault();
    if (!archivo) {
        alert("Por favor selecciona una foto");
        return;
    }

    const formData = new FormData();
    formData.append('titulo', nuevoRecuerdo.titulo);
    formData.append('desc', nuevoRecuerdo.desc);
    formData.append('palabra', nuevoRecuerdo.palabra);
    formData.append('foto', archivo); 

    try {
        // CAMBIO: Agregamos /recuerdos-con-foto y apuntamos a localhost
        const respuesta = await fetch('https://api-recuerdos-nullvoice.onrender.com/recuerdos-con-foto', {          
            method: 'POST',
            body: formData,
        });

        if (respuesta.ok) {
          setNuevoRecuerdo({ titulo: '', desc: '', palabra: '' });
          document.querySelector('input[type="file"]').value = "";
          setArchivo(null);
          traerDatos(); // Esto refrescará la lista local          
        }
    } catch (error) {
        console.error("Error al enviar:", error);
    }
  }


  return (
  <div className="min-h-screen bg-[#2e2829] p-4 md:p-8 font-sans">
    <header className="text-center mb-12">
      <h1 className="text-4xl md:text-6xl font-black text-[#8b84b8] mb-2 tracking-tight">
        Nuestros Recuerdos
      </h1>
      <p className="text-cyan-200 font-medium">Cada línea de código es un momento guardado</p>
    </header>

    {/* Formulario Estilo Card Premium */}
    <form onSubmit={guardarConFoto} className="max-w-md mx-auto bg-white p-6 rounded-3xl shadow-2xl shadow-black mb-16 flex flex-col gap-4 border border-pink-50">
      <h2 className="text-xl font-bold text-gray-800 text-center">Añadir Momento</h2>
      
      <input 
        className="w-full p-4 bg-gray-200 border-none rounded-2xl focus:ring-2 focus:ring-pink-400 outline-none transition-all placeholder:text-gray-400"
        type="text" placeholder="¿Qué nombre le ponemos?" value={nuevoRecuerdo.titulo}
        onChange={(e) => setNuevoRecuerdo({...nuevoRecuerdo, titulo: e.target.value})}
      />
      <textarea 
        className="w-full p-4 bg-gray-200 border-none rounded-2xl focus:ring-2 focus:ring-pink-400 outline-none transition-all placeholder:text-gray-400 min-h-25"
        placeholder="Cuéntame la historia..." value={nuevoRecuerdo.desc}
        onChange={(e) => setNuevoRecuerdo({...nuevoRecuerdo, desc: e.target.value})}
      />
      <input 
        className="w-full p-4 bg-gray-200 border-none rounded-2xl focus:ring-2 focus:ring-pink-400 outline-none transition-all placeholder:text-gray-400"
        type="text" placeholder="Palabra clave (ej: #Cena)" value={nuevoRecuerdo.palabra}
        onChange={(e) => setNuevoRecuerdo({...nuevoRecuerdo, palabra: e.target.value})}
      />
      
      <div className="bg-pink-100 p-4 rounded-2xl border-2 border-dashed border-pink-200">
        <input type="file" onChange={(e) => setArchivo(e.target.files[0])} 
          className="text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-bold file:bg-pink-500 file:text-white hover:file:bg-pink-600 cursor-pointer w-full" 
        />
      </div>

      <button type="submit" className="w-full bg-[#514545] text-white font-black py-4 rounded-2xl hover:bg-[#ff4da6] transform hover:-translate-y-1 transition-all shadow-lg shadow-pink-200">
        ¡GUARDAR RECUERDO!
      </button>
    </form>

    {/* Galería con Grid Inteligente */}
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
      {recuerdos.map((item, index) => (
        <div key={index} className="group bg-white rounded-4xl overflow-hidden shadow-xl hover:shadow-pink-200 transition-all duration-500 hover:-translate-y-2 border border-pink-50">
          <div className="relative h-72 overflow-hidden">
            <img 
              src={item.ruta_foto}
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
              alt={item.titulo}
              onError={(e) => e.target.src = "https://via.placeholder.com/150"} // Esto pone una imagen de error si falla
            />
            <div className="absolute top-4 left-4">
              <span className="bg-white/90 backdrop-blur-sm px-4 py-1.5 rounded-full text-xs font-bold text-pink-500 shadow-sm uppercase tracking-widest">
                #{item.palabra}
              </span>
            </div>
          </div>
          
          <div className="p-8">
            <h3 className="text-2xl font-black text-gray-800 mb-3 leading-tight">{item.titulo}</h3>
            <p className="text-gray-500 leading-relaxed mb-6 italic">"{item.desc}"</p>
            
            <button 
              onClick={() => borrarRecuerdo(item.id)}
              className="w-full py-3 bg-red-50 text-red-500 font-bold rounded-xl border border-red-100 hover:bg-red-500 hover:text-white transition-all duration-300 shadow-sm"
            >
              Eliminar este momento
            </button>
          </div>
        </div>
      ))}
    </div>
  </div>
)
}

export default App