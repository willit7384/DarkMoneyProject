import usMap from "../assets/maps_of_united_states-3402049976.jpg"; // Option 1 (import)

export default function Home() {
  return (
    <div style={{
      textAlign: 'center',
      padding: '2rem',
      maxWidth: '1200px',
      margin: '0 auto'
    }}>
      <h1>Dark Money Project</h1>
      
      <img 
        src={usMap}
        alt="United States map visualizing dark money flows, grants, and nonprofit funding patterns"
        style={{ 
          maxWidth: '100%', 
          height: 'auto', 
          borderRadius: '8px', 
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          margin: '1.5rem 0'
        }}
      />
      
      <p style={{ fontSize: '1.2rem', marginTop: '1.5rem' }}>
        Tracking nonprofit 990 data, grants, donors, and recipients across the United States.
      </p>
      
      {/* Add quick links later */}
      {/* <div style={{ marginTop: '2rem' }}>
        <Link to="/donors">Explore Top Donors</Link> | 
        <Link to="/recipients">Explore Top Recipients</Link>
      </div> */}
    </div>
  );
}