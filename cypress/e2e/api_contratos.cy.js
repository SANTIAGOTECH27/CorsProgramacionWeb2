describe('API Contract Tests - Session 8 & 9', () => {
  const API_BASE = 'http://localhost:5000';

  describe('GET /api/productos', () => {
    it('debe retornar 200 con un arreglo de productos', () => {
      cy.request('GET', API_BASE + '/api/productos').then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.be.an('array');
        response.body.forEach((producto) => {
          expect(producto).to.have.property('id').that.is.a('number');
          expect(producto).to.have.property('nombre').that.is.a('string');
          expect(producto).to.have.property('precio').that.is.a('number');
        });
      });
    });

    it('debe incluir cabeceras de caché (Session 8)', () => {
      cy.request('GET', API_BASE + '/api/productos').then((response) => {
        expect(response.headers).to.have.property('cache-control');
        expect(response.headers['cache-control']).to.include('max-age=60');
        expect(response.headers).to.have.property('etag');
        expect(response.headers).to.have.property('x-cache-status');
      });
    });

    it('la segunda petición debe ser CACHE HIT', () => {
      cy.request('GET', API_BASE + '/api/productos').then(() => {
        cy.request('GET', API_BASE + '/api/productos').then((response2) => {
          expect(response2.headers['x-cache-status']).to.eq('HIT');
        });
      });
    });
  });

  describe('POST /api/productos e Invalidación de Caché', () => {
    it('debe crear un nuevo producto y retornar 201', () => {
      cy.request('POST', API_BASE + '/api/productos', {
        nombre: 'Mouse Inalámbrico',
        precio: 25.50
      }).then((response) => {
        expect(response.status).to.eq(201);
        expect(response.body).to.have.property('id');
        expect(response.body.nombre).to.eq('Mouse Inalámbrico');
        expect(response.body.precio).to.eq(25.50);
      });
    });

    it('la siguiente petición GET debe ser MISS por invalidación manual', () => {
      cy.request('GET', API_BASE + '/api/productos').then((response) => {
        expect(response.headers['x-cache-status']).to.eq('MISS');
      });
    });
  });

  describe('GET /api/estudiantes', () => {
    it('debe retornar un arreglo de estudiantes', () => {
      cy.request('GET', API_BASE + '/api/estudiantes').then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.be.an('array');
        response.body.forEach((estudiante) => {
          expect(estudiante).to.have.property('id').that.is.a('number');
          expect(estudiante).to.have.property('nombre').that.is.a('string');
          expect(estudiante).to.have.property('apellido').that.is.a('string');
          expect(estudiante).to.have.property('edad').that.is.a('number');
        });
      });
    });
  });
});