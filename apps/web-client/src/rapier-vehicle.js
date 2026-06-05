/**
 * raceGPS Rapier 3D Vehicle Physics
 *
 * Wraps Rapier's DynamicRayCastVehicleController for client-side driving.
 * Coordinate system: X=east, Y=up, Z=south (right-handed, matches Rapier defaults).
 */
const METERS_PER_DEG_LAT = 111320;
function metersPerDegLon(lat) {
    return METERS_PER_DEG_LAT * Math.cos((lat * Math.PI) / 180);
}
export class RapierVehicle {
    world;
    vehicle;
    chassis;
    originLat = 0;
    originLon = 0;
    ready = false;
    R;
    async init(originLat, originLon) {
        const mod = await import('@dimforge/rapier3d-compat');
        const R = mod.default ?? mod;
        await R.init();
        this.R = R;
        this.originLat = originLat;
        this.originLon = originLon;
        this.world = new this.R.World({ x: 0, y: -9.81, z: 0 });
        // Ground plane (infinite flat floor)
        const groundBody = this.world.createRigidBody(this.R.RigidBodyDesc.fixed());
        this.world.createCollider(this.R.ColliderDesc.cuboid(5000, 0.1, 5000), groundBody);
        // Chassis: 1.8m wide, 1.4m tall, 4.2m long
        // Arcade tuning: lighter mass for agility, lower center of gravity
        const chassisDesc = this.R.RigidBodyDesc.dynamic()
            .setTranslation(0, 0.8, 0)
            .setCanSleep(false)
            .setAngularDamping(2.5)
            .setLinearDamping(0.3);
        this.chassis = this.world.createRigidBody(chassisDesc);
        this.world.createCollider(this.R.ColliderDesc.cuboid(0.9, 0.5, 2.1)
            .setMassProperties(800, { x: 0, y: -0.2, z: 0 }, { x: 100, y: 100, z: 100 }, { w: 1, x: 0, y: 0, z: 0 })
            .setRestitution(0.1)
            .setFriction(0.6), this.chassis);
        this.vehicle = this.world.createVehicleController(this.chassis);
        this.vehicle.indexUpAxis = 1; // Y is up
        this.vehicle.setIndexForwardAxis = 2; // Z is forward
        const wheelRadius = 0.35;
        const suspensionRest = 0.4;
        const connectionHeight = -0.4;
        // Front-left
        this.vehicle.addWheel({ x: -0.8, y: connectionHeight, z: 1.4 }, { x: 0, y: -1, z: 0 }, { x: 1, y: 0, z: 0 }, suspensionRest, wheelRadius);
        // Front-right
        this.vehicle.addWheel({ x: 0.8, y: connectionHeight, z: 1.4 }, { x: 0, y: -1, z: 0 }, { x: 1, y: 0, z: 0 }, suspensionRest, wheelRadius);
        // Rear-left
        this.vehicle.addWheel({ x: -0.8, y: connectionHeight, z: -1.4 }, { x: 0, y: -1, z: 0 }, { x: 1, y: 0, z: 0 }, suspensionRest, wheelRadius);
        // Rear-right
        this.vehicle.addWheel({ x: 0.8, y: connectionHeight, z: -1.4 }, { x: 0, y: -1, z: 0 }, { x: 1, y: 0, z: 0 }, suspensionRest, wheelRadius);
        // Arcade wheel tuning: forgiving grip, soft suspension, drift-friendly
        for (let i = 0; i < 4; i++) {
            this.vehicle.setWheelSuspensionStiffness(i, 20);
            this.vehicle.setWheelSuspensionCompression(i, 0.4);
            this.vehicle.setWheelSuspensionRelaxation(i, 0.5);
            this.vehicle.setWheelMaxSuspensionTravel(i, 0.4);
            // Higher friction slip = more forgiving, allows controlled drifting
            this.vehicle.setWheelFrictionSlip(i, 2.2);
            this.vehicle.setWheelMaxSuspensionForce(i, 50000);
        }
        this.ready = true;
    }
    update(inputs, dt) {
        if (!this.ready || !this.world || !this.vehicle || !this.chassis || !this.R)
            return;
        // Arcade driving parameters
        const maxSteer = 0.5; // radians — sharp turning for fun
        const maxForce = 3500; // engine force per drive wheel — snappy acceleration
        const brakeForce = 50; // brake impulse — smooth braking
        // Front wheels steer — negate because Rapier positive = left turn,
        // but our inputs.steer = -1 for left, +1 for right.
        this.vehicle.setWheelSteering(0, -inputs.steer * maxSteer);
        this.vehicle.setWheelSteering(1, -inputs.steer * maxSteer);
        // All-wheel drive for better arcade acceleration and climbing
        this.vehicle.setWheelEngineForce(0, inputs.throttle * maxForce * 0.3);
        this.vehicle.setWheelEngineForce(1, inputs.throttle * maxForce * 0.3);
        this.vehicle.setWheelEngineForce(2, inputs.throttle * maxForce * 0.7);
        this.vehicle.setWheelEngineForce(3, inputs.throttle * maxForce * 0.7);
        // Brake all wheels
        const brake = inputs.brake ? brakeForce : 0;
        for (let i = 0; i < 4; i++) {
            this.vehicle.setWheelBrake(i, brake);
        }
        this.vehicle.updateVehicle(dt);
        this.world.step();
        const pos = this.chassis.translation();
        const rot = this.chassis.rotation();
        // Convert Rapier (X=east, Y=up, Z=south) to geo
        const dLat = -pos.z / METERS_PER_DEG_LAT;
        const dLon = pos.x / metersPerDegLon(this.originLat);
        const lat = this.originLat + dLat;
        const lon = this.originLon + dLon;
        // Heading: car faces +Z (south). quaternion to heading.
        // Extract yaw from quaternion.
        const q = rot;
        const yaw = Math.atan2(2 * (q.w * q.y + q.x * q.z), 1 - 2 * (q.y * q.y + q.z * q.z));
        // yaw=0 means south in Rapier. Convert to compass heading: 0=north, clockwise.
        let heading = (180 - (yaw * 180) / Math.PI) % 360;
        if (heading < 0)
            heading += 360;
        const vel = this.chassis.linvel();
        const speed = Math.sqrt(vel.x * vel.x + vel.z * vel.z);
        return { lat, lon, heading, speed, x: pos.x, y: pos.y, z: pos.z };
    }
    reset(lat, lon, headingDeg) {
        if (!this.ready || !this.chassis || !this.vehicle || !this.R)
            return;
        this.originLat = lat;
        this.originLon = lon;
        const x = 0;
        const z = 0;
        // Heading: compass 0=north. south is +Z.
        // yaw = 180° - heading
        const yaw = ((180 - headingDeg) * Math.PI) / 180;
        const halfYaw = yaw / 2;
        const q = { x: 0, y: Math.sin(halfYaw), z: 0, w: Math.cos(halfYaw) };
        this.chassis.setTranslation({ x, y: 1.5, z }, true);
        this.chassis.setRotation(q, true);
        this.chassis.setLinvel({ x: 0, y: 0, z: 0 }, true);
        this.chassis.setAngvel({ x: 0, y: 0, z: 0 }, true);
        for (let i = 0; i < 4; i++) {
            this.vehicle.setWheelEngineForce(i, 0);
            this.vehicle.setWheelBrake(i, 0);
            this.vehicle.setWheelSteering(i, 0);
        }
    }
}
