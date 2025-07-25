/**
 * 定位配置文件
 * 可以在这里自定义办公地址和其他位置信息
 */

// 办公地址配置
const LOCATION_CONFIG = {
    // 主要办公地址
    office: {
        name: '南山高新园',
        address: '深圳市南山区高新南一道',
        lat: 22.5405,
        lng: 113.9344,
        phone: '+86 137-0000-0000',
        email: 'shenzhen@example.com',
        workingHours: '周一至周五 9:00-18:00'
    },
    
    // 备用地址（如果有多个办公地点）
    branches: [
        {
            name: '北京分公司',
            address: '北京市朝阳区望京SOHO',
            lat: 39.9042,
            lng: 116.4074,
            phone: '+86 139-0000-0000',
            email: 'beijing@example.com',
            workingHours: '周一至周五 9:00-18:00'
        },
        {
            name: '深圳分公司',
            address: '深圳市南山区高新南一道',
            lat: 22.5405,
            lng: 113.9344,
            phone: '+86 137-0000-0000',
            email: 'shenzhen@example.com',
            workingHours: '周一至周五 9:00-18:00'
        }
    ],
    
    // 地图配置
    map: {
        defaultZoom: 15,
        mapType: 'amap', // 'amap', 'google', 'baidu'
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
    },
    
    // 导航配置
    navigation: {
        defaultProvider: 'amap', // 'amap', 'google', 'baidu'
        enableRoutePlanning: true,
        showTraffic: true
    }
};

// 导出配置
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LOCATION_CONFIG;
} 