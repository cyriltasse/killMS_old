from pylab import *
import pyrap.tables
import pyrap.images
import pyrap.measures
import pylab
import scipy.optimize

from pyrap.tables import table
from pyrap.images import image

class ClassPierce():
    def __init__(self,antenna_positions,height):
        self.antenna_positions=antenna_positions
        self.me = pyrap.measures.measures()
        p = self.me.position('ITRF', '%fm' % antenna_positions[0,0], '%fm' % antenna_positions[0,1], '%fm' % antenna_positions[0,2])
        self.me.doframe(p)
        self.N_ant=antenna_positions.shape[0]
        self.height=height*1e3
        print "  Class pierce height: %5.1f km"%height

   
    def givePP(self,time,rain,decin,asel=[],giveAir=False,reshape=False):

        if type(rain)==list:
            ra=np.array(rain)
            dec=np.array(decin)
        elif (type(rain)==float)|(len(rain.shape)==0):
            ra=np.array([rain])
            dec=np.array([decin])
        else:
            ra=rain.flatten()
            dec=decin.flatten()
            
        NDir=ra.shape[0]
        if asel==[]: asel=range(self.N_ant)
        N_pp=ra.shape[0]*len(asel)
        
        if giveAir==False:
            piercepoints = zeros((N_pp, 3))
        else:
            piercepoints = zeros((N_pp, 4))
        epoch = self.me.epoch('UTC', '%fs' % time)
        self.me.doframe(epoch)
        pp_idx = 0
        import ClassTimeIt
        T=ClassTimeIt.ClassTimeIt()
        T.disable()
        for i in range(ra.shape[0]):
            d = self.me.direction('J2000', '%frad' % ra[i], '%frad' % dec[i])
            d1 = self.me.measure(d, 'ITRF')
            T.timeit("  P_setdir")
            phi = d1['m0']['value']
            theta = d1['m1']['value']
            dx = cos(theta)*cos(phi)
            dy = cos(theta)*sin(phi)
            dz = sin(theta)
            direction = array((dx,dy,dz))
            for ant_idx in asel:
                pos = self.antenna_positions[ant_idx,:]
                if giveAir==False:
                    piercepoints[pp_idx, :] = self.calc_piercepoint(pos, direction, self.height)
                else:
                    piercepoints[pp_idx, :] = self.getPP(pos, direction, self.height)
                pp_idx = pp_idx + 1
            T.timeit("  P_rest")
        if giveAir==False:
            return piercepoints[:, 0],piercepoints[:, 1],piercepoints[:, 2]
        else:
            if reshape==True:
                return piercepoints[:, 0].reshape(NDir,len(asel)),piercepoints[:, 1].reshape(NDir,len(asel)),\
                    piercepoints[:, 2].reshape(NDir,len(asel)),piercepoints[:, 3].reshape(NDir,len(asel))
            else:
                return piercepoints[:, 0],piercepoints[:, 1],piercepoints[:, 2],piercepoints[:, 3]

    
    def calc_piercepoint(self,pos, direction, height):
        
        pp = zeros(3)
        earth_ellipsoid_a = 6378137.0;
        earth_ellipsoid_a2 = earth_ellipsoid_a*earth_ellipsoid_a;
        earth_ellipsoid_b = 6356752.3142;
        earth_ellipsoid_b2 = earth_ellipsoid_b*earth_ellipsoid_b;
        earth_ellipsoid_e2 = (earth_ellipsoid_a2 - earth_ellipsoid_b2) / earth_ellipsoid_a2;
        
        ion_ellipsoid_a = earth_ellipsoid_a + height;
        ion_ellipsoid_a2_inv = 1.0 / (ion_ellipsoid_a * ion_ellipsoid_a);
        ion_ellipsoid_b = earth_ellipsoid_b + height;
        ion_ellipsoid_b2_inv = 1.0 / (ion_ellipsoid_b * ion_ellipsoid_b);
        
        x = pos[0]/ion_ellipsoid_a;
        y = pos[1]/ion_ellipsoid_a;
        z = pos[2]/ion_ellipsoid_b;
        c = x*x + y*y + z*z - 1.0;
        
        dx = direction[0] / ion_ellipsoid_a
        dy = direction[1] / ion_ellipsoid_a
        dz = direction[2] / ion_ellipsoid_b
        a = dx*dx + dy*dy + dz*dz
        b = x*dx + y*dy  + z*dz
        alpha = (-b + sqrt(b*b - a*c))/a
        pp = pos[0] + alpha*direction
        normal_x = pp[0] * ion_ellipsoid_a2_inv
        normal_y = pp[1] * ion_ellipsoid_a2_inv
        normal_z = pp[2] * ion_ellipsoid_b2_inv
        norm_normal2 = normal_x*normal_x + normal_y*normal_y + normal_z*normal_z
        norm_normal = sqrt(norm_normal2)
        sin_lat2 = normal_z*normal_z / norm_normal2
        g = 1.0 - earth_ellipsoid_e2*sin_lat2
        sqrt_g = sqrt(g)
        M = earth_ellipsoid_b2 / ( earth_ellipsoid_a * g * sqrt_g )
        N = earth_ellipsoid_a / sqrt_g
        
        local_ion_ellipsoid_e2 = (M-N) / ((M+height)*sin_lat2 - N - height);
        local_ion_ellipsoid_a = (N+height) * sqrt(1.0 - local_ion_ellipsoid_e2*sin_lat2)
        local_ion_ellipsoid_b = local_ion_ellipsoid_a*sqrt(1.0 - local_ion_ellipsoid_e2)
        
        z_offset = ((1.0-earth_ellipsoid_e2)*N + height - (1.0-local_ion_ellipsoid_e2)*(N+height)) * sqrt(sin_lat2)
        
        x1 = pos[0]/local_ion_ellipsoid_a
        y1 = pos[1]/local_ion_ellipsoid_a
        z1 = (pos[2]-z_offset)/local_ion_ellipsoid_b
        c1 = x1*x1 + y1*y1 + z1*z1 - 1.0
        
        dx = direction[0] / local_ion_ellipsoid_a
        dy = direction[1] / local_ion_ellipsoid_a
        dz = direction[2] / local_ion_ellipsoid_b
        a = dx*dx + dy*dy + dz*dz
        b = x1*dx + y1*dy  + z1*dz
        alpha = (-b + sqrt(b*b - a*c1))/a
        
        pp = pos + alpha*direction
        return pp


    def getPP(self,mPosition, direction, h):
        R_earth=6364.62e3;
        earth_ellipsoid_a = 6378137.0;
        earth_ellipsoid_a2 = earth_ellipsoid_a*earth_ellipsoid_a;
        earth_ellipsoid_b = 6356752.3142;
        earth_ellipsoid_b2 = earth_ellipsoid_b*earth_ellipsoid_b;
        earth_ellipsoid_e2 = (earth_ellipsoid_a2 - earth_ellipsoid_b2) / earth_ellipsoid_a2;
        posCS002=[3826577.1095  ,461022.900196, 5064892.758]

        stationX = mPosition[0];
        stationY = mPosition[1];
        stationZ = mPosition[2];
    
        ion_ellipsoid_a = earth_ellipsoid_a + h;
        ion_ellipsoid_a2_inv = 1.0 / (ion_ellipsoid_a * ion_ellipsoid_a);
        ion_ellipsoid_b = earth_ellipsoid_b + h;
        ion_ellipsoid_b2_inv = 1.0 / (ion_ellipsoid_b * ion_ellipsoid_b);
        
        x = stationX/ion_ellipsoid_a;
        y = stationY/ion_ellipsoid_a;
        z = stationZ/ion_ellipsoid_b;
        c = x*x + y*y + z*z - 1.0;
    
        dx = direction [0]/ ion_ellipsoid_a;
        dy = direction [1] / ion_ellipsoid_a;
        dz = direction [2] / ion_ellipsoid_b;
    
        a = dx*dx + dy*dy + dz*dz;
        b = x*dx + y*dy  + z*dz;
        alpha = (-b + sqrt(b*b - a*c))/a;
        pp_x = stationX + alpha*direction[0];
        pp_y = stationY + alpha*direction[1]
        pp_z = stationZ + alpha*direction[2];
    
        normal_x = pp_x * ion_ellipsoid_a2_inv;
        normal_y = pp_y * ion_ellipsoid_a2_inv;
        normal_z = pp_z * ion_ellipsoid_b2_inv;
        norm_normal2 = normal_x*normal_x + normal_y*normal_y + normal_z*normal_z;
        norm_normal = sqrt(norm_normal2);
        sin_lat2 = normal_z*normal_z / norm_normal2;
    
     
        g = 1.0 - earth_ellipsoid_e2*sin_lat2;
        sqrt_g = sqrt(g);
    
        M = earth_ellipsoid_b2 / ( earth_ellipsoid_a * g * sqrt_g );
        N = earth_ellipsoid_a / sqrt_g;
    
        local_ion_ellipsoid_e2 = (M-N) / ((M+h)*sin_lat2 - N - h);
        local_ion_ellipsoid_a = (N+h) * sqrt(1.0 - local_ion_ellipsoid_e2*sin_lat2);
        local_ion_ellipsoid_b = local_ion_ellipsoid_a*sqrt(1.0 - local_ion_ellipsoid_e2);
    
        z_offset = ((1.0-earth_ellipsoid_e2)*N + h - (1.0-local_ion_ellipsoid_e2)*(N+h)) * sqrt(sin_lat2);
    
        x1 = stationX/local_ion_ellipsoid_a;
        y1 = stationY/local_ion_ellipsoid_a;
        z1 = (stationZ-z_offset)/local_ion_ellipsoid_b;
        c1 = x1*x1 + y1*y1 + z1*z1 - 1.0;
    
        dx = direction[0] / local_ion_ellipsoid_a;
        dy = direction[1] / local_ion_ellipsoid_a;
        dz = direction[2] / local_ion_ellipsoid_b;
        a = dx*dx + dy*dy + dz*dz;
        b = x1*dx + y1*dy  + z1*dz;
        alpha = (-b + sqrt(b*b - a*c1))/a;
    
        pp_x = stationX + alpha*direction[0];
        pp_y = stationY + alpha*direction[1]
        pp_z = stationZ + alpha*direction[2];
    
        normal_x = pp_x / (local_ion_ellipsoid_a * local_ion_ellipsoid_a);
        normal_y = pp_y / (local_ion_ellipsoid_a * local_ion_ellipsoid_a);
        normal_z = (pp_z-z_offset) / (local_ion_ellipsoid_b * local_ion_ellipsoid_b);
    
        norm_normal2 = normal_x*normal_x + normal_y*normal_y + normal_z*normal_z;
        norm_normal = sqrt(norm_normal2);
        
        pp_airmass = norm_normal / (direction[0]*normal_x + direction[1]*normal_y + direction[2]*normal_z);
    
        return (pp_x,pp_y,pp_z,pp_airmass)
    
