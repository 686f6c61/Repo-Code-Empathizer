"""Tests for TypeScript language analyzer"""
import pytest
from src.language_analyzers.typescript_analyzer import TypeScriptAnalyzer


class TestTypeScriptAnalyzer:
    
    @pytest.fixture
    def analyzer(self):
        return TypeScriptAnalyzer()
    
    def test_file_extensions(self, analyzer):
        assert set(analyzer.get_file_extensions()) == {'.ts', '.tsx'}
    
    def test_language_name(self, analyzer):
        assert analyzer.get_language_name() == 'TypeScript'
    
    def test_type_coverage(self, analyzer):
        code = '''
interface User {
    id: number;
    name: string;
    email: string;
}

function greet(user: User): string {
    return `Hello, ${user.name}!`;
}

function add(a: number, b: number): number {
    return a + b;
}

const untypedFunction = (x, y) => {
    return x + y;
};

let typedVar: string = "hello";
let untypedVar = 42;
'''
        metrics = analyzer.analyze_file('test.ts', code)
        
        assert 'typescript' in metrics
        assert metrics['typescript']['type_coverage'] > 0.5  # Most items are typed
        assert metrics['typescript']['interfaces'] == 1
    
    def test_type_aliases_and_enums(self, analyzer):
        code = '''
type Status = 'active' | 'inactive' | 'pending';
type ID = string | number;

interface Config<T> {
    data: T;
    timestamp: Date;
}

enum Color {
    Red = 'RED',
    Green = 'GREEN',
    Blue = 'BLUE'
}

enum Direction {
    Up,
    Down,
    Left,
    Right
}
'''
        metrics = analyzer.analyze_file('test.ts', code)
        
        assert metrics['typescript']['type_aliases'] == 2
        assert metrics['typescript']['enums'] == 2
        assert metrics['typescript']['interfaces'] == 1
    
    def test_generic_functions(self, analyzer):
        code = '''
function identity<T>(arg: T): T {
    return arg;
}

function map<T, U>(array: T[], fn: (item: T) => U): U[] {
    return array.map(fn);
}

const genericArrow = <T extends object>(obj: T): T => {
    return { ...obj };
};
'''
        functions = analyzer._extract_functions(code)
        
        # Should find generic functions
        function_names = [f['name'] for f in functions]
        assert 'identity' in function_names
        assert 'map' in function_names
    
    def test_decorators(self, analyzer):
        code = '''
class UserController {
    @Get('/users')
    async getUsers(): Promise<User[]> {
        return await this.userService.findAll();
    }
    
    @Post('/users')
    @ValidateBody(UserDto)
    async createUser(@Body() user: UserDto): Promise<User> {
        return await this.userService.create(user);
    }
}
'''
        functions = analyzer._extract_functions(code)
        
        # Should find decorated methods
        function_names = [f['name'] for f in functions]
        assert 'getUsers' in function_names
        assert 'createUser' in function_names
    
    def test_documentation_boost_for_types(self, analyzer):
        well_typed_code = '''
interface Product {
    id: string;
    name: string;
    price: number;
}

function calculateTotal(products: Product[]): number {
    return products.reduce((sum, p) => sum + p.price, 0);
}
'''
        
        poorly_typed_code = '''
function calculateTotal(products) {
    return products.reduce((sum, p) => sum + p.price, 0);
}
'''
        
        well_typed_metrics = analyzer.analyze_file('test.ts', well_typed_code)
        poorly_typed_metrics = analyzer.analyze_file('test.ts', poorly_typed_code)
        
        # Well-typed code should get documentation boost
        assert well_typed_metrics['documentacion']['cobertura'] >= poorly_typed_metrics['documentacion']['cobertura']
    
    def test_security_boost_for_types(self, analyzer):
        typed_code = '''
function processInput(input: string): string {
    return input.trim().toLowerCase();
}

function validateAge(age: number): boolean {
    return age >= 0 && age <= 150;
}
'''
        
        metrics = analyzer.analyze_file('test.ts', typed_code)
        
        # Type safety should boost security score
        assert metrics['seguridad']['validacion'] > 0.5
    
    def test_interface_naming_convention(self, analyzer):
        consistent_with_i = '''
interface IUser {
    name: string;
}

interface IProduct {
    id: number;
}

interface IService {
    fetch(): void;
}
'''
        
        consistent_without_i = '''
interface User {
    name: string;
}

interface Product {
    id: number;
}

interface Service {
    fetch(): void;
}
'''
        
        inconsistent = '''
interface IUser {
    name: string;
}

interface Product {
    id: number;
}

interface IService {
    fetch(): void;
}
'''
        
        consistent_i_metrics = analyzer.analyze_file('test.ts', consistent_with_i)
        consistent_no_i_metrics = analyzer.analyze_file('test.ts', consistent_without_i)
        inconsistent_metrics = analyzer.analyze_file('test.ts', inconsistent)
        
        # Both consistent styles should score higher than inconsistent
        assert consistent_i_metrics['consistencia_estilo']['consistencia'] > inconsistent_metrics['consistencia_estilo']['consistencia']
        assert consistent_no_i_metrics['consistencia_estilo']['consistencia'] > inconsistent_metrics['consistencia_estilo']['consistencia']